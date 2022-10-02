import email
import os
import json
import requests
# import creds
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_login import LoginManager, LoginForm, login_user
login_manager = LoginManager()

basedir = os.path.abspath(os.path.dirname(__file__)) # absolute path of current dir

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # uses less memory

db = SQLAlchemy(app)

# ROUTES

@app.route('/')
@app.route('/login/', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.get(form.email.data)
        if user:
            # bcrypt.check_password_hash(user.password, form.password.data)
            # if user.password == form.password.data:
                user.authenticated = True
                # db.session.add(user)
                # db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for('home.html'))
    return render_template('login.html')

@login_manager.user_loader
def user_loader(user_id): return User.query.get(user_id)

@app.route('/register/', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        new_user = User(firstname = firstname, lastname = lastname, email = email)
        db.session.add(new_user)
        db.session.commit()
        return "Boop boop you're registered!"
    return render_template('register.html')

@app.route('/logout/', methods=["GET"])
def logout():
    return 'Logout'

@app.route('/home/')
def home():
    return render_template('home.html')

@app.route('/books/')
def books():
    return render_template('books.html')

@app.route('/search/')
def search():
    books = []
    if 'book' in request.args:
        search_word = request.args.get('book')
        link = 'https://www.googleapis.com/books/v1/volumes?q='
        link += search_word
        link += '&key='
        link += creds.google_books_api
        response = requests.get(link)
        data = json.loads(response.content)
        books = data['items']
    return render_template('dev_book_search.html', books=books)

