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
      name TEXT NOT NULL,
      email TEXT UNIQUE,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      password TEXT NOT NULL DEFAULT ''
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT,
      description TEXT NOT NULL,
      amount INT NOT NULL,
      date TEXT NOT NULL,
      category TEXT NOT NULL,
      user_id INTEGER,
      FOREIGN KEY (user_id) REFERENCES users(id) 
    )
    """)

    conn.commit() #saves changes
    conn.close() # closes the connection IMPORTANT~!

@app.post("/api/expenses")
def create_expense():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    date = data.get("date")
    category = data.get("category")
    user_id = data.get("user_id")

    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided to create an expense"
        }), 400


    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (title, description, amount, date, category, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, amount, date, category, user_id))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Expense created successfully"}), 201

@app.get("/api/health")
def health_check():
    return jsonify({"status": "OK"}), 200

@app.post("/api/register")
def register():
    data = request.get_json() #retrieves the data sent from the user
    print(data)
    user = data.get("name")
    email = data.get("email")
    password = data.get("password")


    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (user, email, password))
    conn.commit()
    conn.close()

    return jsonify({"message": "User registered successfully"}), 201

@app.get("/api/users")
def get_users():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Allow columns to be retrived by name (e.g. row['name'])
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, FROM users") #can add email, and password
    rows = cursor.fetchall() #List of users objects
    print(rows)
    conn.close()

    users = []
    for row in rows:
        user = {"id": row["id"], "name": row["name"]}
        users.append(user)

    return jsonify({
        "success": True,
        "message": "Users retrieved successfully",
        "data": users
    }), 200

# http://127.0.0.1:5000/api/users/2
@app.get("/api/users/<int:user_id>")
def get_user_by_id(user_id):
    conn =  sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    #Validation to check if user exists
    cursor.execute("SELECT id, name FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    print(row["name"])
    conn.close()

    return jsonify({
        "success": True,
        "message": "User retrieved successfully",
        "data": {"id": row["id"], "name": row["name"]}
    }), 200


@app.delete("/api/users/<int:user_id>") #RESTful API design
def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Validation to check if user exists
    cursor.execute("SELECT id, name FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "User deleted successfully"
    }), 200

@app.put("/api/users/<int:user_id>")
def update_user(user_id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = ?, email = ?, password = ? WHERE id = ?", (name, email, password, user_id))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "User updated successfully"
    }), 200


@app.get("/api/expenses")
def get_expenses():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    conn.close()

    expenses = []
    for row in rows:
        expense = {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "amount": row["amount"],
            "date": row["date"],
            "category": row["category"],
            "user_id": row["user_id"]
        }
        expenses.append(expense)

    return jsonify({
        "success": True,
        "message": "Expenses retrieved successfully",
        "data": expenses
    }), 200


@app.get("/api/expenses/<int:expense_id>")
def get_expense_by_id(expense_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()
    conn.close()
    print(row)

    

    if not row:
        return jsonify({
            "success": False,
            "message": "Expense not found"
        }), 404

    # expense = {
    #     "id": row["id"],
    #     "title": row["title"],
    #     "description": row["description"],
    #     "amount": row["amount"],
    #     "date": row["date"],
    #     "category": row["category"],
    #     "user_id": row["user_id"]
    # }

    return jsonify({
        "success": True,
        "message": "Expense retrieved successfully",
        "data": expense_id
    }), 200


@app.delete("/api/expenses/<int:expense_id>")
def delete_expense(expense_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Validation to check if expense exists
    cursor.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({
            "success": False,
            "message": "Expense not found"
        }), 404

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Expense deleted successfully"
    }), 200


@app.put("/api/expenses/<int:expense_id>")
def update_expense(expense_id):
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    date = data.get("date")
    category = data.get("category")
    user_id = data.get("user_id")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        if not data:
            return jsonify({"error": "No data provided"}), 400  


        cursor.execute("""
            UPDATE expenses
            SET title = ?, description = ?, amount = ?, date = ?, category = ?, user_id = ?
            WHERE id = ?
        """, (title, description, amount, date, category, user_id, expense_id))
        conn.commit()
        return jsonify({
                "success": True,
                "message": "Expense updated successfully"
            }), 200

    except sqlite3.IntegrityError as e:
        # IntegrityError is most likely when an attribute has specific constraints
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 400

    except sqlite3.OperationalError as e:
        # OperationalError is most likely when the SQL syntax is wrong
        return jsonify({"error": f"Database operational error: {str(e)}"}), 500

    except sqlite3.DatabaseError as e:
        # DatabaseError is a generic error for database related issues
        return jsonify({
            "error": f"Database error: {e.sqlite_errorcode}: {str(e)}"
        }), 500

    finally:
        conn.close()



if __name__ == '__main__':
    init_db()
    app.run(debug=True)