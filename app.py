from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)

# ✅ IMPORTANT FIX: stable secret key (Render safe)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_secret_key_123")

# ✅ session fix for mobile + Render
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = True


# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        type TEXT,
        item TEXT,
        description TEXT
    )''')

    conn.commit()
    conn.close()

init_db()


# ---------------- HOME ----------------
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                      (username, password))
            conn.commit()
        except:
            return "User already exists"

        conn.close()
        return redirect("/login")

    return render_template("signup.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session.clear()
            session["user"] = username
            return redirect("/dashboard")

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        item_type = request.form["type"]
        item = request.form["item"]
        desc = request.form["description"]

        c.execute("INSERT INTO items (username, type, item, description) VALUES (?, ?, ?, ?)",
                  (session["user"], item_type, item, desc))
        conn.commit()

    c.execute("SELECT * FROM items ORDER BY id DESC")
    items = c.fetchall()

    conn.close()

    return render_template("dashboard.html", user=session["user"], items=items)


if __name__ == "__main__":
    app.run()