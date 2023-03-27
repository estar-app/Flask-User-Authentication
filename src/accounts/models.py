from datetime import datetime


from flask_login import UserMixin

from src import bcrypt, db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime




class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, email, password, is_admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.created_on = datetime.now()
        self.is_admin = is_admin

    def __repr__(self):
        return f"<email {self.email}>"


# Define the Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.String(1000))
    bot_response = db.Column(db.String(1000))
    text = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    content = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Message(id={self.id}, user_message={self.user_message}, bot_response={self.bot_response})"




