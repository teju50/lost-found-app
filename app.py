from flask import Flask, render_template, request, redirect, session, url_for
users = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email in users and users[email]["password"] == password:
            session["user"] = email
            return redirect("/dashboard")
        return "Invalid login"

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        users[email] = {"name": name, "password": password}
        return redirect("/login")

    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

@app.route("/upload")
def upload():
    if "user" not in session:
        return redirect("/login")
    return render_template("upload.html")

@app.route("/item")
def item():
    return render_template("item.html")

@app.route("/edit")
def edit():
    return render_template("edit.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
