import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# In-memory store — resets on every restart
trips_store = {}
next_id = 1


# ── routes ─────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/trips", methods=["GET"])
def list_trips():
    result = []
    for trip in sorted(trips_store.values(), key=lambda t: t["created_at"], reverse=True):
        t = dict(trip)
        t["tourist_count"] = len(t.get("tourists", []))
        t["created_at"] = t["created_at"].strftime("%d %b %Y")
        result.append(t)
    return jsonify(result)


@app.route("/api/trips", methods=["POST"])
def create_trip():
    global next_id
    data = request.json
    trip_id = next_id
    next_id += 1
    trips_store[trip_id] = {
        "id":               trip_id,
        "destination":      data["destination"],
        "duration_days":    data["duration_days"],
        "transport_type":   data["transport_type"],
        "transport_detail": data.get("transport_detail", ""),
        "cost_transport":   data["cost_transport"],
        "cost_hotel":       data["cost_hotel"],
        "cost_food":        data["cost_food"],
        "cost_tickets":     data["cost_tickets"],
        "cost_guide":       data["cost_guide"],
        "cost_misc":        data["cost_misc"],
        "split_method":     data["split_method"],
        "total_cost":       data["total_cost"],
        "tourists":         data.get("tourists", []),
        "created_at":       datetime.now(),
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
