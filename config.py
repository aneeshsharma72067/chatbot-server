import os

class Config:
    """Base Configuration"""
    SQLALCHEMY_DATABASE_URI = "postgres+psycopg2://default:NweKl3HzJy9n@ep-shiny-shape-a4x2upf1-pooler.us-east-1.aws.neon.tech:5432/verceldb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = 'production'
    SECRET_KEY = os.getenv('SECRET_KEY')
