import email
import os
import json
import requests
import creds
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__)) # absolute path of current dir

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # uses less memory

db = SQLAlchemy(app)

# ROUTES

@app.route('/')
@app.route('/login/')
def login():
    return render_template('login.html')

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

@app.route('/logout/')
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

# DATABASES

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
 
    # gives each object a recognisable string representation for debugging purposes
    # def __repr__(self):
    #     return f'<User {self.email}>'

class Follower(db.Model):
    # A follows B
    id = db.Column(db.Integer, primary_key=True)
    user_A_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable = False)
    user_B_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable = False)

class BooksRecomended(db.Model):
    # A recomended book to B
    # B must follow A
    id = db.Column(db.Integer, primary_key=True)
    user_A_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable = False)
    user_B_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable = False)
    book_id = db.Column(db.String(12), nullable = False)