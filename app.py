from flask import Flask, render_template, request, redirect, session
from datetime import timedelta
from werkzeug.utils import secure_filename
import os
import json

import cloudinary
import cloudinary.uploader

# ✅ FIXED: Use CLOUDINARY_URL from environment
cloudinary.config(secure=True)

DATA_FILE = "data.json"
app = Flask(__name__)

# ---------------- CONFIG ----------------
app.secret_key = "secret123"
app.permanent_session_lifetime = timedelta(days=7)

UPLOAD_FOLDER = "static/uploads"
USER_FILE = "users.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- USERS ----------------
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# ---------------- ITEMS ----------------
def load_items():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_items(items):
    with open(DATA_FILE, "w") as f:
        json.dump(items, f)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        users = load_users()

        email = request.form["email"]

        users[email] = {
            "name": request.form["name"],
            "password": request.form["password"]
        }

        save_users(users)
        return redirect("/login")

    return render_template("signup.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()

        email = request.form["email"]
        password = request.form["password"]

        if email in users and users[email]["password"] == password:
            session.permanent = True
            session["user"] = email
            return redirect("/dashboard")

        return "❌ Invalid login"

    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

# ---------------- UPLOAD ----------------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        file = request.files.get("image")

        if not file or file.filename == "":
            return "❌ No file selected"

        result = cloudinary.uploader.upload(file)
        image_url = result['secure_url']

        items = load_items()

        new_item = {
            "id": len(items),
            "name": request.form["name"],
            "type": request.form["type"],
            "description": request.form["description"],
            "contact": request.form["contact"],
            "location": request.form["location"],
            "image": image_url
        }

        items.append(new_item)
        save_items(items)

        return redirect("/items")

    return render_template("upload.html")

# ---------------- ITEMS ----------------
@app.route("/items")
def items():
    if "user" not in session:
        return redirect("/login")

    items = load_items()
    return render_template("items.html", items=items)

# ---------------- EDIT ----------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if "user" not in session:
        return redirect("/login")

    items = load_items()

    if id >= len(items):
        return "Item not found"

    if request.method == "POST":
        items[id]["name"] = request.form["name"]
        items[id]["type"] = request.form["type"]
        items[id]["description"] = request.form["description"]
        items[id]["contact"] = request.form["contact"]
        items[id]["location"] = request.form["location"]

        file = request.files.get("image")
        if file and file.filename != "":
            result = cloudinary.uploader.upload(file)
            items[id]["image"] = result['secure_url']

        save_items(items)

        return redirect("/items")

    return render_template("edit.html", item=items[id], id=id)

# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete(id):
    if "user" not in session:
        return redirect("/login")

    items = load_items()

    if id < len(items):
        items.pop(id)
        save_items(items)

    return redirect("/items")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)