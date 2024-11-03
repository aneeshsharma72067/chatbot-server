from flask import Flask
from flask_cors import CORS
from config import Config
from app.model import db
from app.routes import bp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
CORS(app,resources={r"/*":{"origins":"http://localhost:3000"}},supports_credentials=True)

app.register_blueprint(bp)

with app.app_context():
    db.create_all()