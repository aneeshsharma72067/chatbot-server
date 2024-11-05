import os

class Config:
    """Base Configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv('POSTGRES_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = 'production'
    JWT_SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'