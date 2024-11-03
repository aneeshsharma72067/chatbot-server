from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import uuid
import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    
    chats = db.relationship('Chat', backref='user', lazy=True)

    def __repr__(self) -> str:
        return f"User('{self.username}, {self.created_at}')"

class Chat(db.Model):
    __tablename__ = 'chats'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())
    
    messages = db.relationship('Message', backref='chat', lazy=True, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Chat('{self.title}, {self.created_at}')"

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = db.Column(db.String(36), db.ForeignKey('chats.id'), nullable=False)
    sender = db.Column(db.String(50), nullable=False)  # e.g., 'user' or 'bot'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())

    def __repr__(self) -> str:
        return f"Message('{self.sender}', '{self.content}, {self.created_at}')"

