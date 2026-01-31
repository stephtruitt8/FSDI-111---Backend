from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DB_NAME = "budget_manager.db"

def init_db():
    conn = sqlite3.connect(DB_NAME) #opens a connection to the database
    cursor = conn.cursor() #creates a cursor/tool that lets us send commands

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit() #saves changes
    conn.close() # closes the connection IMPORTANT~!

@app.get("/api/health")
def health_check():
    return jsonify({"status": "OK"}), 200

@app.post("/api/register")
def register():
    data = request.get_json() #retrieves the data sent from the user
    print(data)
    user = data.get("name")
    email = data.get("email")


    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (user, email))
    conn.commit()
    conn.close()

    return jsonify({"message": "User registered successfully"}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True)