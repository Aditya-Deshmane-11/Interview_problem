from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import mysql.connector

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 🔹 MySQL connection (phpMyAdmin / XAMPP)
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",        # XAMPP default
        database="interview_tracking"
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/live-counts")
def live_counts():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT decision, COUNT(*)
        FROM responses
        GROUP BY decision
    """)
    rows = cur.fetchall()

    cur.close()
    db.close()

    counts = {
        "Accepted": 0,
        "Rejected": 0,
        "Not Able to Pick": 0,
        "Not Able to Access Mail": 0
    }

    for decision, count in rows:
        counts[decision] = count

    return jsonify(counts)


@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("""
            INSERT INTO responses
            (username, email, mode, interview_type, decision)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data["username"],
            data["email"],
            data["mode"],
            data["type"],
            data["decision"]
        ))
        db.commit()
    except mysql.connector.IntegrityError:
        return jsonify({"error": "User already submitted"}), 400
    finally:
        cur.close()
        db.close()

    socketio.emit("update")
    return jsonify({"success": True})

def get_db():
    return mysql.connector.connect(
        host="db4free.net",
        user="adityadeshmane",
        password="Aditya#123",
        database="responses",
        port=3306
    )


@app.route("/stats")
def stats():
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT interview_type, decision, COUNT(*)
        FROM responses
        GROUP BY interview_type, decision
    """)
    rows = cur.fetchall()
    cur.close()
    db.close()

    result = {
        "Prime/Digital": {},
        "Ninja": {}
    }

    for itype, decision, count in rows:
        result.setdefault(itype, {})
        result[itype][decision] = count

    return jsonify(result)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)

