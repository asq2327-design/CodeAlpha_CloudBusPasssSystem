from flask import Flask, render_template, request, jsonify
import sqlite3
import secrets
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "buspass.db"

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

ROUTES = {
    "Delhi - Jaipur": 550,
    "Delhi - Chandigarh": 450,
    "Delhi - Amritsar": 700,
    "Chandigarh - Amritsar": 350,
    "Jaipur - Udaipur": 500,
}

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_ref TEXT NOT NULL UNIQUE,
                passenger_name TEXT NOT NULL,
                email TEXT NOT NULL,
                route TEXT NOT NULL,
                travel_date TEXT NOT NULL,
                seats INTEGER NOT NULL CHECK(seats BETWEEN 1 AND 6),
                price_per_seat INTEGER NOT NULL,
                total_price INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'CONFIRMED',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def generate_ref():
    return "CAP-" + secrets.token_hex(4).upper()

@app.route("/")
def index():
    return render_template("index.html", routes=ROUTES)

@app.get("/api/routes")
def routes():
    return jsonify([
        {"route": name, "price": price}
        for name, price in ROUTES.items()
    ])

@app.post("/api/bookings")
def create_booking():
    data = request.get_json(silent=True) or {}
    name = str(data.get("passenger_name", "")).strip()
    email = str(data.get("email", "")).strip()
    route = str(data.get("route", "")).strip()
    travel_date = str(data.get("travel_date", "")).strip()

    try:
        seats = int(data.get("seats", 1))
    except (TypeError, ValueError):
        seats = 0

    if not all([name, email, route, travel_date]):
        return jsonify({"error": "All fields are required."}), 400
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"error": "Enter a valid email address."}), 400
    if route not in ROUTES:
        return jsonify({"error": "Invalid route."}), 400
    if seats < 1 or seats > 6:
        return jsonify({"error": "Seats must be between 1 and 6."}), 400

    try:
        datetime.strptime(travel_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Travel date must be YYYY-MM-DD."}), 400

    price_per_seat = ROUTES[route]
    total_price = price_per_seat * seats

    # The price is always calculated on the server from the trusted route table.
    for _ in range(5):
        ref = generate_ref()
        try:
            with get_db() as conn:
                conn.execute(
                    """INSERT INTO bookings
                    (booking_ref, passenger_name, email, route, travel_date,
                     seats, price_per_seat, total_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (ref, name, email, route, travel_date, seats,
                     price_per_seat, total_price)
                )
            break
        except sqlite3.IntegrityError:
            continue
    else:
        return jsonify({"error": "Could not create booking reference."}), 500

    return jsonify({
        "status": "CONFIRMED",
        "booking_ref": ref,
        "route": route,
        "travel_date": travel_date,
        "seats": seats,
        "price_per_seat": price_per_seat,
        "total_price": total_price
    }), 201

@app.get("/api/bookings/<booking_ref>")
def get_booking(booking_ref):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM bookings WHERE booking_ref = ?",
            (booking_ref.upper(),)
        ).fetchone()
    if not row:
        return jsonify({"error": "Booking not found."}), 404
    return jsonify(dict(row))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=True)
