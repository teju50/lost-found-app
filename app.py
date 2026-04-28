from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- USERS (temporary storage) ----------------
users = {"admin": "1234"}

# ---------------- DATABASE MODEL ----------------
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    type = db.Column(db.String(20))
    location = db.Column(db.String(100))
    contact = db.Column(db.String(50))
    image = db.Column(db.String(100))

with app.app_context():
    db.create_all()

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['user'] = username
            return redirect('/items')

    return render_template('login.html')

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            return "User already exists!"

        users[username] = password
        return redirect('/')

    return render_template('signup.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ---------------- SHOW ITEMS ----------------
@app.route('/items')
def items():
    if 'user' not in session:
        return redirect('/')

    all_items = Item.query.all()
    return render_template('items.html', items=all_items)

# ---------------- UPLOAD ----------------
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        file = request.files['image']
        filename = file.filename
        file.save(os.path.join('static', filename))

        new_item = Item(
            title=request.form['title'],
            type=request.form['type'],
            location=request.form['location'],
            contact=request.form['contact'],
            image=filename
        )

        db.session.add(new_item)
        db.session.commit()

        return redirect('/items')

    return render_template('upload.html')

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    item = Item.query.get(id)
    db.session.delete(item)
    db.session.commit()
    return redirect('/items')

# ---------------- EDIT ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    item = Item.query.get(id)

    if request.method == 'POST':
        item.title = request.form['title']
        item.type = request.form['type']
        item.location = request.form['location']
        item.contact = request.form['contact']

        db.session.commit()
        return redirect('/items')

    return render_template('edit.html', item=item)

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)