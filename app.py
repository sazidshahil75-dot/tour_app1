import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# In-memory store — resets on every restart
trips_store = {}
next_id = 1

AUTO_DELETE_DAYS = 14  # trips older than this are purged


def purge_old_trips():
    """Remove trips older than AUTO_DELETE_DAYS."""
    cutoff = datetime.now() - timedelta(days=AUTO_DELETE_DAYS)
    stale = [tid for tid, t in trips_store.items() if t["created_at"] < cutoff]
    for tid in stale:
        del trips_store[tid]


# ── routes ─────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/trips", methods=["GET"])
def list_trips():
    purge_old_trips()
    result = []
    for trip in sorted(trips_store.values(), key=lambda t: t["created_at"], reverse=True):
        t = dict(trip)
        t["tourist_count"] = len(t.get("tourists", []))
        created = t["created_at"]
        t["created_at"] = created.strftime("%d %b %Y")
        # days remaining before auto-delete
        expires = created + timedelta(days=AUTO_DELETE_DAYS)
        remaining = (expires - datetime.now()).days
        t["expires_in_days"] = max(0, remaining)
        result.append(t)
    return jsonify(result)


@app.route("/api/trips", methods=["POST"])
def create_trip():
    global next_id
    purge_old_trips()
    data = request.json
    trip_id = next_id
    next_id += 1
    trips_store[trip_id] = {
        "id":                   trip_id,
        "destination":          data["destination"],
        "duration_days":        data["duration_days"],
        "transport_type":       data["transport_type"],
        "transport_detail":     data.get("transport_detail", ""),
        "cost_transport":       data["cost_transport"],
        "cost_hotel":           data["cost_hotel"],
        "cost_food":            data["cost_food"],
        "cost_tickets":         data["cost_tickets"],
        "cost_guide":           data["cost_guide"],
        "cost_misc":            data["cost_misc"],
        "split_method":         data["split_method"],
        "total_cost":           data["total_cost"],
        "tourists":             data.get("tourists", []),
        # ── accommodation fields ──
        "accom_name":           data.get("accom_name", ""),
        "accom_type":           data.get("accom_type", ""),
        "accom_address":        data.get("accom_address", ""),
        "accom_checkin":        data.get("accom_checkin", ""),
        "accom_checkout":       data.get("accom_checkout", ""),
        "accom_room_type":      data.get("accom_room_type", ""),
        "accom_rooms":          data.get("accom_rooms", ""),
        "accom_booking_ref":    data.get("accom_booking_ref", ""),
        "accom_phone":          data.get("accom_phone", ""),
        "accom_notes":          data.get("accom_notes", ""),
        "created_at":           datetime.now(),
    }
    return jsonify({"id": trip_id, "message": "Trip saved!"})


@app.route("/api/trips/<int:trip_id>", methods=["GET"])
def get_trip(trip_id):
    trip = trips_store.get(trip_id)
    if not trip:
        return jsonify({"error": "Not found"}), 404
    t = dict(trip)
    t["created_at"] = t["created_at"].strftime("%d %b %Y")
    return jsonify(t)


@app.route("/api/trips/<int:trip_id>", methods=["DELETE"])
def delete_trip(trip_id):
    trips_store.pop(trip_id, None)
    return jsonify({"message": "Deleted"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
