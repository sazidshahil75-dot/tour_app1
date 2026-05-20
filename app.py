import os
import mysql.connector
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Railway injects these environment variables automatically
# when you add a MySQL plugin to your project.
DB_CONFIG = {
    "host":     os.environ.get("MYSQLHOST",     "localhost"),
    "port":     int(os.environ.get("MYSQLPORT", 3306)),
    "user":     os.environ.get("MYSQLUSER",     "root"),
    "password": os.environ.get("MYSQLPASSWORD", ""),
    "database": os.environ.get("MYSQLDATABASE", "railway"),
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    """Create tables if they don't exist. Called once at startup."""
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id               INT AUTO_INCREMENT PRIMARY KEY,
            destination      VARCHAR(255)  NOT NULL,
            duration_days    INT           NOT NULL DEFAULT 1,
            transport_type   VARCHAR(100),
            transport_detail VARCHAR(255),
            cost_transport   DECIMAL(12,2) DEFAULT 0,
            cost_hotel       DECIMAL(12,2) DEFAULT 0,
            cost_food        DECIMAL(12,2) DEFAULT 0,
            cost_tickets     DECIMAL(12,2) DEFAULT 0,
            cost_guide       DECIMAL(12,2) DEFAULT 0,
            cost_misc        DECIMAL(12,2) DEFAULT 0,
            split_method     VARCHAR(50)   DEFAULT 'equal',
            total_cost       DECIMAL(12,2) DEFAULT 0,
            created_at       DATETIME      DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tourists (
            id           INT AUTO_INCREMENT PRIMARY KEY,
            trip_id      INT           NOT NULL,
            name         VARCHAR(255)  NOT NULL,
            share_pct    DECIMAL(6,2)  DEFAULT 0,
            share_amount DECIMAL(12,2) DEFAULT 0,
            FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    db.commit()
    cur.close()
    db.close()


# Auto-create tables at startup
with app.app_context():
    try:
        init_db()
        print("Database tables ready.")
    except Exception as e:
        print(f"DB init warning: {e}")


# ── routes ─────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/trips", methods=["GET"])
def list_trips():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT t.*, COUNT(p.id) AS tourist_count
        FROM trips t
        LEFT JOIN tourists p ON p.trip_id = t.id
        GROUP BY t.id
        ORDER BY t.created_at DESC
    """)
    trips = cur.fetchall()
    for tr in trips:
        if isinstance(tr.get("created_at"), datetime):
            tr["created_at"] = tr["created_at"].strftime("%d %b %Y")
    cur.close(); db.close()
    return jsonify(trips)


@app.route("/api/trips", methods=["POST"])
def create_trip():
    data = request.json
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO trips
          (destination, duration_days, transport_type, transport_detail,
           cost_transport, cost_hotel, cost_food, cost_tickets,
           cost_guide, cost_misc, split_method, total_cost)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        data["destination"], data["duration_days"],
        data["transport_type"], data.get("transport_detail", ""),
        data["cost_transport"], data["cost_hotel"],
        data["cost_food"],      data["cost_tickets"],
        data["cost_guide"],     data["cost_misc"],
        data["split_method"],   data["total_cost"],
    ))
    trip_id = cur.lastrowid
    for t in data.get("tourists", []):
        cur.execute("""
            INSERT INTO tourists (trip_id, name, share_pct, share_amount)
            VALUES (%s, %s, %s, %s)
        """, (trip_id, t["name"], t["share_pct"], t["share_amount"]))
    db.commit()
    cur.close(); db.close()
    return jsonify({"id": trip_id, "message": "Trip saved!"})


@app.route("/api/trips/<int:trip_id>", methods=["GET"])
def get_trip(trip_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM trips WHERE id=%s", (trip_id,))
    trip = cur.fetchone()
    if not trip:
        cur.close(); db.close()
        return jsonify({"error": "Not found"}), 404
    if isinstance(trip.get("created_at"), datetime):
        trip["created_at"] = trip["created_at"].strftime("%d %b %Y")
    cur.execute("SELECT * FROM tourists WHERE trip_id=%s ORDER BY id", (trip_id,))
    trip["tourists"] = cur.fetchall()
    cur.close(); db.close()
    return jsonify(trip)


@app.route("/api/trips/<int:trip_id>", methods=["DELETE"])
def delete_trip(trip_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM tourists WHERE trip_id=%s", (trip_id,))
    cur.execute("DELETE FROM trips WHERE id=%s",         (trip_id,))
    db.commit()
    cur.close(); db.close()
    return jsonify({"message": "Deleted"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
