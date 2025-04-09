import re
from ollama import chat
from flask import Flask, request, jsonify, render_template, session, make_response
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import json, os
import uuid
import datetime
import database
import hashlib
from datetime import timedelta
from SPOTIPYLINKTEST import create_playlist
#logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='../client/static', template_folder='../client/templates')
app.secret_key = "your_secret_key"  # Needed to store session data
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "messages.db")}'
db = SQLAlchemy(app)

class allUsers(db.Model):
    __tablename__ = 'allusers'
    user_id = db.Column(db.String(64), primary_key=True)
    password = db.Column(db.String(64))

class UserHistory(db.Model):
    __tablename__ = 'user_history'
    message_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(64), db.ForeignKey('allusers.user_id'), nullable=False)
    message = db.Column(db.Text)
    role = db.Column(db.String)
    session_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()


# Your hash functions
def make_hash(password):
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    return "$".join([algorithm, salt, password_hash])

def verify_hash(stored_hash, input_password):
    parts = stored_hash.split('$')
    if len(parts) != 3:
        return False
    algorithm, salt, _ = parts
    hash_obj = hashlib.new(algorithm)
    hash_obj.update((salt + input_password).encode('utf-8'))
    return stored_hash == "$".join([algorithm, salt, hash_obj.hexdigest()])

@app.route("/generate_songs", methods=["POST"])
def generate_songs():
    #get user input / user id from the frontend 
    user_input = request.json.get("content")
    user_id = None
    if session['is_guest'] == True:
        user_id = request.json.get("userId") #guest using cookie
    else:
        user_id = session['username']  #signed-in user 

   
    existing_user = allUsers.query.filter_by(user_id=user_id).first()
    if not existing_user:
        new_user = allUsers(user_id=user_id)
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
            "make a playlist that fits this description: " + user_input + """Respond in this exact format, and include at least 30 songs: 
            "<playlist title>
            <artist>: <title>, 
            <artist>: <title>, 
            <artist>: <title>, 
            ..."
            Here is an example to follow:
            "Chill Pop Songs
            Taylor Swift: Lover,
            Gracie Abrams: Packing it Up,
            Taylor Swift: Champagne Problems,
            Ed Sheeran: Lego House" """

        else: #if new user 
            user_input = "Make a playlist that fits this description: " + user_input
            user_input = user_input + """Respond in this exact format, and include at least 30 songs: 
                "<playlist title>,
                <artist>: <title>, 
                <artist>: <title>, 
                <artist>: <title>, 
                ..."
                Here is an example to follow:
                "Chill Pop Songs,
                Taylor Swift: Lover,
                Gracie Abrams: Packing it Up,
                Taylor Swift: Champagne Problems,
                Ed Sheeran: Lego House" """

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
    
    #FOR DEBUG
    #f = open("demofile1.txt", "a")
    #f.write(str(response))
    #f.close()

    
    # Parse response to get songs in form {'playlist_title': title, 'songs': [(artist, title), (artist, title)...]}
    playlist = parse_output(response)
    print(playlist) 
    
    #FOR DEBUG 
    #f = open("demofile2.txt", "a")
    #f.write(playlist)
    #f.close()


    link = create_playlist(playlist)
    #for debugging
    #test_playlist = {'playlist_title': 'TEST', 'songs':[('Pink Floyd', 'Pigs (Three Different Ones)'),('Pink Floyd', 'Wish You Were Here'),('Pink Floyd', 'Dogs'), ('Pink Floyd', 'Have a Cigar'), ('Pink Floyd', 'Time')]}
    #FOR DEBUGGING
    #f = open("demofile2.txt", "a")
    #f.write(test_playlist['songs'][0][1])
    #f.close()
    #link = create_playlist(test_playlist)


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
    playlist_title = lines[0].replace("Playlist Title:", "").strip()
    playlist_title = re.sub(r'[^a-zA-Z0-9\s]', '', playlist_title)
    
    for line in lines[1:]:
        artist, title = map(str.strip, line.split(":", 1)) 
        artist = re.sub(r'[^a-zA-Z0-9\s]', '', artist)
        title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        songs.append((artist, title))
    
    # print("parsing!")
    
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


@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html', username=session.get('username'), is_guest=session.get('is_guest', False))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username and password:
            user = database.get_user(username)
            if user and verify_hash(user['password'], password):
                session['username'] = username
                session['is_guest'] = False
                return redirect(url_for('home'))
        
        flash('Invalid username or password', 'error')
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/guest-login')
def guest_login():
    session['username'] = 'Guest'
    session['is_guest'] = True
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=24)
    return redirect(url_for('home'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('create_account'))
        
        if database.user_exists(username):
            flash('Username already exists', 'error')
            return redirect(url_for('create_account'))
        
        hashed_password = make_hash(password)
        database.add_user(username, hashed_password)
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('create_account.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8000)
