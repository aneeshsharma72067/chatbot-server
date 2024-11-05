from flask import Blueprint, request, jsonify, make_response
from app.model import Chat, User, Message, db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from sqlalchemy import desc
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

bp = Blueprint('main',__name__)


load_dotenv()

genai.configure(api_key=os.getenv('GOOGLE_GENAI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')


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

        access_token = create_access_token(identity=new_user.id)
        resp = make_response({"message": "User registered successfully","token":access_token, "user":{"username":new_user.username,"id":new_user.id,"created_at":new_user.created_at}})
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
        access_token = create_access_token(identity=user.id)
        resp = make_response({"message": "Login successful", "token":access_token, "user":{"username":user.username,"id":user.id,"created_at":user.created_at}})
        return resp
    return jsonify({"error": "Invalid credentials"}), 401

@bp.route('/test', methods=['GET'])
def test():
    return jsonify({'msg':'hey'}),200

@bp.route('/auth-check', methods=['GET'])
@jwt_required()
def checkAuth():
    try:
        user_id = get_jwt_identity()
        if user_id is None:
            print('User ID not found in token')
            return jsonify({"error":"User ID not found in token"}), 400
        user =  User.query.filter_by(id=user_id).first() 
        return jsonify({"user":{"username":user.username,"id":user.id,"created_at":user.created_at}}) 
    
    except Exception as e:
        print(e)
        return jsonify({"error": "Something went wrong !!"}), 401

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"message": "Logged out successfully"})


@bp.route('/chats', methods=['POST'])
@jwt_required()
def create_chat():
    try:
        user_id = get_jwt_identity()
        
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
@jwt_required()
def get_chats():
    try:
        user_id = get_jwt_identity()
        if not user_id:
            print('user id not found')
            return {'error':"User id not found"}, 400

        chats = Chat.query.filter_by(user_id=user_id).order_by(desc(Chat.created_at)).all()
        chat_list = [{"id": chat.id, "title": chat.title, 'created_at':chat.created_at} for chat in chats]
        return jsonify(chat_list), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Something Went Wrong"}), 401
    
@bp.route('/chats/<chat_id>', methods=['PUT'])
@jwt_required()
def rename_chat(chat_id):
    try:
        user_id = get_jwt_identity()
        
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
@jwt_required()
def delete_chat(chat_id):
    chat = Chat.query.filter_by(id=chat_id).first()
    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    db.session.delete(chat)
    db.session.commit()

    return jsonify({"message": "Chat deleted successfully"}), 200 



@bp.route('/chats/<chat_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(chat_id):

    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at).all()
    return jsonify([{
        "id": msg.id,
        "sender": msg.sender,
        "content": msg.content,
        "created_at": msg.created_at
    } for msg in messages]), 200


@bp.route('/chats/<chat_id>/messages', methods=['POST'])
@jwt_required()
def send_message(chat_id):
   
    data = request.json
    content = data.get('content')

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
    

    # Call GPT-3 API asynchronously 
    bot_response = gpt3_request(content)  
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
    try:
        response = model.generate_content(user_message)
        if response.text:
            return response.text
        elif response.candidates[0].finish_reason == 'SAFETY':
            return "Violet or sexually explicit content is not allowed"
    except Exception as e:
        return "Something Went Wrong"