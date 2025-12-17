from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secure_notepad_secret"

def get_db():
    return sqlite3.connect("database.db")

# Create tables
with get_db() as db:
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content TEXT
        ) 
    """)
    db.commit()

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        try:
            with get_db() as db:
                db.execute("INSERT INTO users (username, password) VALUES (?,?)",
                           (username, password))
                db.commit()
            return redirect("/login")
        except:
            return "Username already exists!"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            return redirect("/dashboard")
        else:
            return "Invalid Credentials!"

    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    db = get_db()

    if request.method == "POST":
        note = request.form["note"]
        db.execute("INSERT INTO notes (user_id, content) VALUES (?,?)",
                   (user_id, note))
        db.commit()

    notes = db.execute("SELECT * FROM notes WHERE user_id=?", (user_id,)).fetchall()
    return render_template("dashboard.html", notes=notes)

@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" in session:
        with get_db() as db:
            db.execute("DELETE FROM notes WHERE id=?", (id,))
            db.commit()
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
