from flask import Blueprint, request, jsonify, make_response
from app.model import Chat, User, Message, db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from config import Config
from functools import wraps
import datetime
from sqlalchemy import desc
import google.generativeai as genai
import os
from dotenv import load_dotenv

bp = Blueprint('main',__name__)


load_dotenv()

genai.configure(api_key=os.getenv('GOOGLE_GENAI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('auth_token')
        
        if not token:
            return jsonify({"error" : "Unathorized"}),400  # Redirect to login if no token is found

        try:
            # Verify the token
            jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)  # Proceed to the route if token is valid
    
    return decorated_function



@bp.route('/', methods=['GET'])
def index():
    return {"message":"AI Chatbot Assistant API"}

@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400

    try:    
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()

        token = jwt.encode({"user_id": new_user.id, "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)}, Config.SECRET_KEY, algorithm="HS256")

        resp = make_response({"message": "User registered successfully", "user":{"username":new_user.username,"id":new_user.id,"created_at":new_user.created_at}})
        expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
        resp.set_cookie('auth_token', token, httponly=True, secure=True,expires=expires,max_age=86400)
        return resp, 201
    except:
        return jsonify({"error":"Something went wrong"}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        token = jwt.encode({"user_id": user.id, "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)}, Config.SECRET_KEY, algorithm="HS256")
        resp = make_response({"message": "Login successful", "user":{"username":user.username,"id":user.id,"created_at":user.created_at}})
        expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
        resp.set_cookie('auth_token', token, httponly=True, secure=True,expires=expires,max_age=86400)
        return resp
    return jsonify({"error": "Invalid credentials"}), 401

@bp.route('/test', methods=['GET'])
def test():
    return jsonify({'msg':'hey'}),200

@bp.route('/auth-check', methods=['GET'])
def checkAuth():
    token = request.cookies.get('auth_token')  # Retrieve the JWT from the cookie
    
    if not token:
        return jsonify({"error": "Unauthorized"}), 400

    try:
        # Decode the JWT to verify its validity
        decoded_token = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get("user_id")
        if user_id is None:
            return jsonify({"error":"User ID not found in token"}), 400
        # Retrieve user data (from a database, here we use a placeholder)
        user =  User.query.filter_by(id=user_id).first() # Example user data
        return jsonify({"user":{"username":user.username,"id":user.id,"created_at":user.created_at}})  # Return user data if the token is valid
    
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

@bp.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({"message": "Logged out successfully"}))
    response.set_cookie("auth_token", "", expires=0)  # Setting expires=0 removes the cookie
    return response


@bp.route('/chats', methods=['POST'])
@login_required
def create_chat():
    token = request.cookies.get('auth_token')
    if not token:
        return jsonify({"error": "Auth Token Not found"}), 401
    try:
        decoded_token = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get("user_id")
        
        data = request.json
        title = data.get('title')
        
        new_chat = Chat(user_id=user_id, title=title)
        db.session.add(new_chat)
        db.session.commit()
        return jsonify({"id": new_chat.id, "title": new_chat.title, 'user_id':user_id, 'created_at':new_chat.created_at}), 201
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401


@bp.route('/chats', methods=['GET'])
@login_required
def get_chats():
    token = request.cookies.get('auth_token')
    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        decoded_token = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get("user_id")

        chats = Chat.query.filter_by(user_id=user_id).order_by(desc(Chat.created_at)).all()
        chat_list = [{"id": chat.id, "title": chat.title, 'created_at':chat.created_at} for chat in chats]
        return jsonify(chat_list), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    
@bp.route('/chats/<chat_id>', methods=['PUT'])
@login_required
def rename_chat(chat_id):
    token = request.cookies.get('auth_token')
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        decoded_token = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get("user_id")
        
        chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()
        if not chat:
            return jsonify({"error": "Chat not found or you do not have permission to rename it"}), 404
        
        data = request.json
        new_title = data.get('title')
        
        chat.title = new_title
        db.session.commit()
        
        return jsonify({"message":"Chat title updated"}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401



@bp.route('/chats/<chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    chat = Chat.query.filter_by(id=chat_id).first()
    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    # Delete the chat
    db.session.delete(chat)
    db.session.commit()

    return jsonify({"message": "Chat deleted successfully"}), 200 



@bp.route('/chats/<chat_id>/messages', methods=['GET'])
@login_required
def get_messages(chat_id):

    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at).all()
    return jsonify([{
        "id": msg.id,
        "sender": msg.sender,
        "content": msg.content,
        "created_at": msg.created_at
    } for msg in messages]), 200


@bp.route('/chats/<chat_id>/messages', methods=['POST'])
@login_required
def send_message(chat_id):
   
    data = request.json
    content = data.get('content')

    # Save the user message
    new_message = Message(chat_id=chat_id, sender='user', content=content)
    db.session.add(new_message)
    db.session.commit()

    response_data = {
            "user_message": {
                "id": new_message.id,
                "content": new_message.content,
                "sender": "user",
                "chat_id": new_message.chat_id,
                "created_at": new_message.created_at
            }
        }
    

    # Call GPT-3 API asynchronously (placeholder code)
    bot_response = gpt3_request(content)  # This function should call the GPT-3 API
    bot_message = Message(chat_id=chat_id, sender='bot', content=bot_response)
    db.session.add(bot_message)
    db.session.commit()

    response_data["bot_message"] = {
        "id": bot_message.id,
        "content": bot_message.content,
        "sender": "bot",
        "chat_id": bot_message.chat_id,
        "created_at": bot_message.created_at
    }

    return jsonify(response_data), 200


def gpt3_request(user_message: str):
    # This function should make a request to the GPT-3 API and return a response
    try:
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        return "Something Went Wrong"