import os

class Config:
    """Base Configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv('POSTGRES_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = 'production'
    SECRET_KEY = os.getenv('SECRET_KEY')
