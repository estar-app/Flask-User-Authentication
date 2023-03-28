from datetime import datetime


from flask_login import UserMixin

from src import bcrypt, db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime



class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
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
        return f"<User(email={self.email})>"


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_message = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    bot_response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    text = db.Column(db.String(255))

    user = db.relationship('User', backref=db.backref('messages', lazy=True))

    def __init__(self, user, user_message, created_at=None):
        self.user = user
        self.user_message = user_message
        if created_at:
            self.created_at = created_at

    def __repr__(self):
        return f"Message(id={self.id}, user_message={self.user_message}, bot_response={self.bot_response})"


class ChatHistory(db.Model):
    __tablename__ = 'chat_history'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String)
    message = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"ChatHistory(id={self.id}, user={self.user}, message={self.message})"

