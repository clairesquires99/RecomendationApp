from . import db

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        return True

    def get_id(self):
        return self.user_id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False
 
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