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


    #retrieve any messages if returning user  
    saved_messages = []
    history = UserHistory.query.filter_by(user_id=user_id).all()
    for msg in history:
        saved_messages.append({'role': msg.role, 'content': msg.message})


    
    if "session_id" not in session: #if no SESSION history (first message)
        if saved_messages: #if previous user
            user_input = "Considering the general vibe and general preferences of all previous messages, " \
            "make a playlist that fits this description: " + user_input

        else: #if new user 
            user_input = "Make a playlist that fits this description: " + user_input
            user_input = user_input + """If you add commentary, only do so BEFORE the list. After the commentary, 
    write "Playlist title: <playlist title>".
    Then, respond with the list of songs, which should be formatted as such: 
    <artist>: <title>, one song per line, separated by A SINGLE NEWLINE and NO extra characters.
    DO NOT add any commentary after the end of the list. Reply in that exact format."""

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

    # Generate response using Ollama
    response = chat(model='llama3.2', messages=saved_messages)

    AI_message = UserHistory(user_id=user_id, message=response['message']['content'], role='assistant', session_id=session['session_id'])
    db.session.add(AI_message)
    db.session.commit()
    
    # Save session
    session.modified = True

    # Return the latest response only
    return jsonify({"playlist": response['message']['content']})

def parse_output(response):
    output = response['message']['content']
    lines = output.strip().split("\n")
    songs = []
    playlist_title = lines[0].replace("Playlist title:", "").strip()
    
    for line in lines[1:]:
        artist, title = map(str.strip, line.split(":", 1)) 
        songs.append((artist, title))
    
    print("parsing!")
    
    # note: for spotify's api, you need to pass in an array of spotify uris as strings.
    # in integration part, should extract the following list of songs and search them using the api
    # to get their uris first
    return {
        "playlist_title": playlist_title,
        "songs": songs
    }

    
@app.route("/reset", methods=["POST"])
def reset():
    #session.pop("messages", None)
    session.pop("session_id", None)
    return jsonify({"message": "Conversation history cleared!"})


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8000)










#!/usr/bin/env python3

#OPENAI (and DeepSeek)

# from openai import OpenAI
# client = OpenAI(
#   api_key=""
# )

# completion = client.chat.completions.create(
#   model="gpt-4o-mini",
#   max_tokens=50,
#   store=True,
#   messages=[
#     {"role": "user", "content": "write a haiku about ai"}
#   ]
# )
# print(completion.choices[0].message);


#HUGGINGFACE

# import requests

# # Hugging Face API URL for the model
# token = ''
# #try BERT or T5 models then finetune with music data 

# API_URL = "https://api-inference.huggingface.co/models/gpt2" 

# # Your Hugging Face API token
# headers = {
#     "Authorization": f"Bearer {token}"  # Add token here
# }

# def query(payload):
#     response = requests.post(API_URL, headers=headers, json=payload)
#     return response.json()

# input_data = {
#     "inputs": "What are three popular love songs?"  
# }

# # Call the API and print the response
# response = query(input_data)
# print(response)

#OLLAMA 
# first run: ollama pull llama3.2 in terminal 






# response: ChatResponse = chat(model='llama3.2', messages=[
#   {
#     'role': 'user',
#     'content': 'can you give me a playlist with kendrick lamar songs and ariana grande songs and taylor swift songs. But only 5 songs total?',
#   },
# ])
# print(response['message']['content'])
