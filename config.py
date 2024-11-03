import os

class Config:
    """Base Configuration"""
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:root@localhost/chatbot"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = 'development'
    SECRET_KEY = os.getenv('SECRET_KEY')