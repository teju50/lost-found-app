from flask import Flask, render_template, request, redirect, session, url_for
import os

app = Flask(__name__)

# IMPORTANT: change this in production
app.secret_key = "back2you_super_secure_key"

# Fake user storage (for now)
users = {}

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        users[email] = {
            "name": name,
            "password": password
        }

        return redirect(url_for("login"))

    return render_template("signup.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email in users and users[email]["password"] == password:
            session["user"] = email
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")


# ---------------- UPLOAD ----------------
@app.route("/upload")
def upload():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("upload.html")


# ---------------- ITEM PAGE ----------------
@app.route("/item")
def item():
    return render_template("item.html")


# ---------------- EDIT PAGE ----------------
@app.route("/edit")
def edit():
    return render_template("edit.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)