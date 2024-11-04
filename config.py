import os

class Config:
    """Base Configuration"""
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:root@localhost/chatbot"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = 'development'
    JWT_SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'