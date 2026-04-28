from flask import Flask, render_template, request, redirect, session
import os, json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

USER_FILE = "users.json"

# ---------------- USER STORAGE ----------------
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

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

# ---------------- LOGIN (FIXED MEMORY ISSUE) ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()   # 🔥 always reload latest data

        email = request.form["email"]
        password = request.form["password"]

        if email in users and users[email]["password"] == password:
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

# ---------------- ITEMS ----------------
items = []

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        file = request.files["image"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        item = {
            "id": len(items),
            "name": request.form["name"],
            "type": request.form["type"],
            "description": request.form["description"],
            "contact": request.form["contact"],
            "location": request.form["location"],
            "image": filename
        }

        items.append(item)

        return redirect("/items")

    return render_template("upload.html")

@app.route("/items")
def items_page():
    return render_template("items.html", items=items)

@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit(item_id):
    item = items[item_id]

    if request.method == "POST":
        item["name"] = request.form["name"]
        item["type"] = request.form["type"]
        item["description"] = request.form["description"]
        item["contact"] = request.form["contact"]
        item["location"] = request.form["location"]
        return redirect("/items")

    return render_template("edit.html", item=item)

@app.route("/delete/<int:item_id>")
def delete(item_id):
    items.pop(item_id)
    return redirect("/items")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)