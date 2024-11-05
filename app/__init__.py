from flask import Flask
from flask_cors import CORS
from config import Config
from app.model import db
from app.routes import bp
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
jwt = JWTManager(app)
CORS(app, supports_credentials=True)
app.register_blueprint(bp)


with app.app_context():
    db.create_all()