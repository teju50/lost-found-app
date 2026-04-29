from flask import Flask, render_template, request, redirect, session
from datetime import timedelta
import os
import cloudinary
import cloudinary.uploader
from pymongo import MongoClient
from bson.objectid import ObjectId

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secret123")
app.permanent_session_lifetime = timedelta(days=7)

# MongoDB connection
client = MongoClient(os.environ.get("MONGO_URI"))
db = client["back2you"]
users_col = db["users"]
items_col = db["items"]

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        if users_col.find_one({"email": email}):
            return "❌ Email already registered"
        users_col.insert_one({
            "email": email,
            "name": request.form["name"],
            "password": request.form["password"]
        })
        return redirect("/login")
    return render_template("signup.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = users_col.find_one({"email": email, "password": password})
        if user:
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

        items_col.insert_one({
            "name": request.form["name"],
            "type": request.form["type"],
            "description": request.form["description"],
            "contact": request.form["contact"],
            "location": request.form["location"],
            "image": image_url,
            "uploaded_by": session["user"]
        })

        return redirect("/items")

    return render_template("upload.html")

# ---------------- ITEMS ----------------
@app.route("/items")
def items():
    if "user" not in session:
        return redirect("/login")
    all_items = list(items_col.find())
    for item in all_items:
        item["id"] = str(item["_id"])
    return render_template("items.html", items=all_items)

# ---------------- EDIT ----------------
@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    if "user" not in session:
        return redirect("/login")

    item = items_col.find_one({"_id": ObjectId(id)})
    if not item:
        return "Item not found"

    if request.method == "POST":
        update = {
            "name": request.form["name"],
            "type": request.form["type"],
            "description": request.form["description"],
            "contact": request.form["contact"],
            "location": request.form["location"],
        }
        file = request.files.get("image")
        if file and file.filename != "":
            result = cloudinary.uploader.upload(file)
            update["image"] = result['secure_url']

        items_col.update_one({"_id": ObjectId(id)}, {"$set": update})
        return redirect("/items")

    item["id"] = str(item["_id"])
    return render_template("edit.html", item=item, id=item["id"])

# ---------------- DELETE ----------------
@app.route("/delete/<id>")
def delete(id):
    if "user" not in session:
        return redirect("/login")
    items_col.delete_one({"_id": ObjectId(id)})
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