# ================================
# STEP 1: IMPORT LIBRARIES
# ================================
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

# ================================
# STEP 2: INITIALIZE FLASK APP
# ================================
app = Flask(__name__)
CORS(app)  # allows frontend to connect

DB_NAME = "tickets.db"


# ================================
# STEP 3: DATABASE CONNECTION
# ================================
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ================================
# STEP 4: CREATE TABLES
# ================================
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            date TEXT NOT NULL,
            total_tickets INTEGER NOT NULL,
            available_tickets INTEGER NOT NULL
        )
    """)

    # Bookings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            user_name TEXT,
            tickets_booked INTEGER,
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)

    conn.commit()
    conn.close()


create_tables()


# ================================
# STEP 5: ADD EVENT (ADMIN)
# ================================
@app.route("/add_event", methods=["POST"])
def add_event():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO events (name, location, date, total_tickets, available_tickets)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["name"],
        data["location"],
        data["date"],
        data["total_tickets"],
        data["total_tickets"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Event added successfully"}), 201


# ================================
# STEP 6: GET ALL EVENTS
# ================================
@app.route("/events", methods=["GET"])
def get_events():
    conn = get_db_connection()
    events = conn.execute("SELECT * FROM events").fetchall()
    conn.close()

    return jsonify([dict(event) for event in events])


# ================================
# STEP 7: BOOK TICKETS
# ================================
@app.route("/book_ticket", methods=["POST"])
def book_ticket():
    data = request.json
    event_id = data["event_id"]
    user_name = data["user_name"]
    tickets = data["tickets"]

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check availability
    event = cursor.execute(
        "SELECT available_tickets FROM events WHERE id = ?",
        (event_id,)
    ).fetchone()

    if not event:
        return jsonify({"error": "Event not found"}), 404

    if event["available_tickets"] < tickets:
        return jsonify({"error": "Not enough tickets available"}), 400

    # Update tickets
    cursor.execute("""
        UPDATE events
        SET available_tickets = available_tickets - ?
        WHERE id = ?
    """, (tickets, event_id))

    # Save booking
    cursor.execute("""
        INSERT INTO bookings (event_id, user_name, tickets_booked)
        VALUES (?, ?, ?)
    """, (event_id, user_name, tickets))

    conn.commit()
    conn.close()

    return jsonify({"message": "Tickets booked successfully"}), 200


# ================================
# STEP 8: VIEW BOOKINGS
# ================================
@app.route("/bookings", methods=["GET"])
def get_bookings():
    conn = get_db_connection()
    bookings = conn.execute("""
        SELECT bookings.id, user_name, tickets_booked, events.name
        FROM bookings
        JOIN events ON bookings.event_id = events.id
    """).fetchall()
    conn.close()

    return jsonify([dict(booking) for booking in bookings])


# ================================
# STEP 9: RUN SERVER
# ================================
if __name__ == "__main__":
    app.run(debug=True)
import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))