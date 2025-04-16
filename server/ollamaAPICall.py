import base64
import http
import random
import string
import re
import time
from urllib.parse import quote, urlencode
from ollama import chat
from flask import Flask, request, jsonify, render_template, session, make_response
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import json, os
import uuid
import datetime
import database
import hashlib
from datetime import datetime, timedelta, timezone
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    print(saved_messages)


    if "session_id" not in session: #if no SESSION history (first message)
        if saved_messages: #if previous user
            user_input = "Considering the general vibe and general preferences of all previous messages, " \
            "Absolutely DO NOT converse with me. You can only respond with a playlist. Just make a playlist that fits this description: " + user_input + """Respond in this exact format, and include at least 30 songs. DO NOT INCLUDE ANY OTHER NOTES: 
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
            user_input = "Absolutely DO NOT converse with me. You can only respond with a playlist. Just make me a playlist that fits this description: " + user_input
            user_input = user_input + """Respond in this exact format, and include at least 30 songs. DO NOT INCLUDE ANY OTHER NOTES: 
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
    
    # Parse response to get songs in form {'playlist_title': title, 'songs': [(artist, title), (artist, title)...]}
    try:
        playlist = parse_output(response)
        print(playlist)
        session["parsed_response"] = playlist
    except:
        print('error with parsing')
        new_message = """Repeat the previous command. Remember to respond in this exact format.
                DO NOT INCLUDE ANY OTHER NOTES: 
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
        saved_messages.append({'role': 'user', 'content': new_message})
        response = chat(model='llama3.2', messages=saved_messages)
        playlist = parse_output(response)
        session["parsed_response"] = playlist
    
    #FOR DEBUG 
    #f = open("demofile2.txt", "a")
    #f.write(playlist)
    #f.close()

    # authorize spotify
    # print("authorizing spotify")
    # spotify_auth()
    
    # link = create_playlist(playlist)
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
    # print(output)
    playlist_title = lines[0].replace("Playlist Title:", "").strip()
    playlist_title = re.sub(r'[^a-zA-Z0-9\s]', '', playlist_title)
    
    for line in lines[1:]:
        print(line)
        if line:
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
    
@app.route('/create_playlist', methods=["GET", "POST"])
def create_playlist():
    if is_authorized():
        print("creating playlist!")
        parsed_response = session["parsed_response"]

        ACCESS_TOKEN = get_valid_token()
        PLAYLIST_LINK = ""
        if ACCESS_TOKEN:
            # TODO: get user ID
            USER_ID = get_user_id(ACCESS_TOKEN)
            
            # POST request to create playlist
            conn = http.client.HTTPSConnection("api.spotify.com")
            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }

            playlist_data = {
                "name": parsed_response['playlist_title'], #changed it to this so that the playlist names are variable
                "description": "Made by Jukebot",
                "public": False
            }

            body = json.dumps(playlist_data)
            conn.request("POST", f"/v1/users/{USER_ID}/playlists", body, headers)

            response = conn.getresponse()
            data = json.loads(response.read().decode())
            
            # Get the playlist link and ID
            PLAYLIST_LINK = data.get("external_urls", {}).get("spotify")
            PLAYLIST_ID = data.get("id", {})
            if PLAYLIST_LINK and PLAYLIST_ID:
                print(f"Playlist Created! Link:{PLAYLIST_LINK}, ID:{PLAYLIST_ID}")
            else:
                print("Error creating playlist:", data)
                
            # Add songs to playlist
            add_songs_to_playlist(parsed_response, ACCESS_TOKEN, PLAYLIST_ID)
            session["latest_playlist"] = PLAYLIST_LINK
            
            return jsonify({'playlist_link': PLAYLIST_LINK, 'playlist_title': playlist_data["name"]})
    else:
        return jsonify({'requires_auth': True})

def is_authorized():
    access_token = get_valid_token()
    if access_token:
        return True
    else:
        return False
    
def get_user_id(access_token):
    # Make request to Spotify API to get user id
    conn = http.client.HTTPSConnection("api.spotify.com")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    conn.request("GET", "/v1/me", headers=headers)
    response = conn.getresponse()
    print(response)
    user_data = json.loads(response.read().decode())

    USER_ID = ""
    # Extract the user ID
    if "id" in user_data:
        USER_ID = user_data["id"]
        print(f"Your Spotify User ID: {USER_ID}")
    else:
        print("Error fetching user ID:", user_data)
        
    return USER_ID

def add_songs_to_playlist(parsed_response, access_token, playlist_id):
    # This has been made with the assumption that what it's being given is a list of song titles. 
    #This shouldnt need changing, but a function to convert whatever is given into a list may be needed
    for i in range(0, len(parsed_response['songs'])):
        time.sleep(1) # bc of rate limit
        TRACK_NAME = parsed_response['songs'][i][1]
        ARTIST_NAME = parsed_response['songs'][i][0] 

        query = quote(f"{TRACK_NAME} {ARTIST_NAME}")

        # Make request to Spotify API to get the song URI
        conn = http.client.HTTPSConnection("api.spotify.com")
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        conn.request("GET", f"/v1/search?q={query}&type=track&limit=1" , headers=headers)
        response = conn.getresponse()
        data = json.loads(response.read().decode())

        TRACK_URI = ""
        if "tracks" in data and "items" in data["tracks"] and len(data["tracks"]["items"]) > 0:
            TRACK_URI = data["tracks"]["items"][0]["uri"]
            print(f"Found Track, URI: {TRACK_URI}")
        else:
            print("No track found for query:", TRACK_NAME)
            
        # Add song(s) to the created playlist
        conn = http.client.HTTPSConnection("api.spotify.com")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        uris = [TRACK_URI]
        body = json.dumps({"uris": uris})

        conn.request("POST", f"/v1/playlists/{playlist_id}/tracks", body, headers)

        response = conn.getresponse()
        data = json.loads(response.read().decode())

        if "snapshot_id" in data:
            print("Track added successfully!")
        else:
            print("Error adding track:", data)
    return

# authorize spotify user
@app.route('/spotify_auth', methods=["GET", "POST"])
def spotify_auth():
    print("authorizing")
    # if not is_authorized():
    CLIENT_ID = "6b592b7992754aaca6646d68afc5ccd2" # currently hardcoded
    state = generate_random_string(16);
    scope = 'user-read-private user-read-email playlist-modify-public playlist-modify-private';
    
    auth_query_params = urlencode({
        "response_type": "code",
        "redirect_uri": "http://localhost:8000/callback",
        "scope": scope,
        "state": state,
        "show_dialog": 'true',
        "client_id": CLIENT_ID,
    })
    url = "https://accounts.spotify.com/authorize?" + auth_query_params
    print(url)
    return redirect(url)
    # else:
    #     return redirect(url_for('create_playlist'))
    
def get_credentials():
    client_id = "6b592b7992754aaca6646d68afc5ccd2"
    client_secret = "d3ea681734b34b08a8f2eeff6f27413b"
    return base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

def generate_random_string(length=12):
    characters = string.ascii_letters + string.digits 
    return ''.join(random.choices(characters, k=length))

# receive callback from spotify authorization to exchange code for token
@app.route('/callback', methods=["GET", "POST"])
def spotify_callback():
    print("callback!")
    REDIRECT_URI = "http://localhost:8000/callback"
    code = request.args.get("code")
    state =  request.args.get("state")
    
    if code and state:
        conn = http.client.HTTPSConnection("accounts.spotify.com")
        credentials = get_credentials()
        
        headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        body = urlencode({
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        })

        conn.request("POST", "/api/token", body, headers)
        response = conn.getresponse()
        data = json.loads(response.read().decode())

        ACCESS_TOKEN = data.get("access_token")
        session['access_token'] = ACCESS_TOKEN
        session['token_saved_at'] = datetime.now(timezone.utc).isoformat()
        print("Access Token:", ACCESS_TOKEN)
        
    return redirect("https://www.spotify.com")

def get_valid_token():
    token = session.get('access_token')
    saved_at_str = session.get('token_saved_at')

    if token and saved_at_str:
        saved_at = datetime.fromisoformat(saved_at_str)

        # make sure it's timezone-aware
        if saved_at.tzinfo is None:
            saved_at = saved_at.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        if now - saved_at < timedelta(hours=1):
            return token
        else:
            session.pop('access_token', None)
            session.pop('token_saved_at', None)
            return None
    return None

    
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
