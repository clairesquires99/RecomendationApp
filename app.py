import os
from flask import Flask, render_template, request, url_for, redirect
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
@app.route('/home/')
def home():
    return render_template('home.html')

@app.route('/books/')
def books():
    return render_template('books.html')

# DATABASES

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
 
    # gives each object a recognisable string representation for debugging purposes
    def __repr__(self):
        return f'<User {self.email}>'