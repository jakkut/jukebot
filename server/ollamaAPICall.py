from ollama import chat
from flask import Flask, request, jsonify, render_template, session, make_response
from flask_sqlalchemy import SQLAlchemy
import json, os
import uuid
import datetime
#logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='../client/static', template_folder='../client/templates')
app.secret_key = "your_secret_key"  # Needed to store session data
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "messages.db")}'
db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(64), primary_key=True)
    password = db.Column(db.String(64))

class UserHistory(db.Model):
    __tablename__ = 'user_history'
    message_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(64), db.ForeignKey('users.user_id'), nullable=False)
    message = db.Column(db.Text)
    role = db.Column(db.String)
    session_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_songs", methods=["POST"])
def generate_songs():
    #get user input / user id from the frontend 
    user_input = request.json.get("content")
    user_id = request.json.get("userId")

    #save user if new user 
    existing_user = Users.query.filter_by(user_id=user_id).first()
    if not existing_user:
        new_user = Users(user_id=user_id)
        db.session.add(new_user)
        db.session.commit()


    #retrive any messages if returning user  
    saved_messages = []
    history = UserHistory.query.filter_by(user_id=user_id).all()
    for msg in history:
        print(msg.message)
        saved_messages.append({'role': msg.role, 'content': msg.message})


    
    if "session_id" not in session: #if no SESSION history (first message)
        if saved_messages: #if previous user
            user_input = "Considering the general vibe and general preferences of all previous messages, " \
            "make a playlist that fits this description: " + user_input

        else: #if new user 
            user_input = "Make a playlist that fits this description: " + user_input
        
        user_message = UserHistory(user_id=user_id, message=user_input, role='user')
        db.session.add(user_message)
        db.session.commit()

        # save newly created session_id
        recent_history = UserHistory.query.filter_by(user_id=user_id).order_by(UserHistory.created_at.desc()).first()
        session["session_id"] = recent_history.session_id 

    else: #if continuing conversation 
        #no change to user input 
        user_message = UserHistory(user_id=user_id, message=user_input, role='user', session_id=session['session_id'])
        db.session.add(user_message)
        db.session.commit()


    # Append user message
    saved_messages.append({'role': 'user', 'content': user_input})
    print(saved_messages)

    # Generate response using Ollama
    response = chat(model='llama3.2', messages=saved_messages)

    AI_message = UserHistory(user_id=user_id, message=response['message']['content'], role='assistant', session_id=session['session_id'])
    db.session.add(AI_message)
    db.session.commit()
    
    # Save session
    session.modified = True

    # Return the latest response only
    return jsonify({"playlist": response['message']['content']})

@app.route("/reset", methods=["POST"])
def reset():
    #session.pop("messages", None)
    session.pop("session_id", None)
    return jsonify({"message": "Conversation history cleared!"})


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8000)
