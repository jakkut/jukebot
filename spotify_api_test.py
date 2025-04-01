import http.client
import json
import base64
from urllib.parse import urlencode
import webbrowser

import urllib

# 1. Set up API endpoint using Spotify Developer Dashboard (for now, add your own)
CLIENT_ID = 
CLIENT_SECRET = 
REDIRECT_URI = "https://www.spotify.com"

# Encode credentials in base64
credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

# 2. Authenticate user and get access token which authorizes user to make API requests
AUTH_URL = "https://accounts.spotify.com/authorize" # Spotify's authentication URL (asks for manual login)
SCOPE = "playlist-modify-private playlist-modify-public" # Scopes needed for playlist creation

# Auto opens the browser for user authentication
params = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE
}

auth_url = f"{AUTH_URL}?{urlencode(params)}"
webbrowser.open(auth_url)

# Prompt the user to paste the authorization code from the URL
AUTHORIZATION_CODE = input("Paste the authorization code from the redirected URL: ")
conn = http.client.HTTPSConnection("accounts.spotify.com")
headers = {
    "Authorization": f"Basic {credentials}",
    "Content-Type": "application/x-www-form-urlencoded"
}
body = urllib.parse.urlencode({
    "grant_type": "authorization_code",
    "code": AUTHORIZATION_CODE,
    "redirect_uri": REDIRECT_URI,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
})

conn.request("POST", "/api/token", body, headers)
response = conn.getresponse()
data = json.loads(response.read().decode())

ACCESS_TOKEN = data.get("access_token")
print("Access Token:", ACCESS_TOKEN)

# Make request to Spotify API to get user id
conn = http.client.HTTPSConnection("api.spotify.com")
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

conn.request("GET", "/v1/me", headers=headers)
response = conn.getresponse()
user_data = json.loads(response.read().decode())

USER_ID = ""
# Extract the user ID
if "id" in user_data:
    USER_ID = user_data["id"]
    print(f"Your Spotify User ID: {USER_ID}")
else:
    print("Error fetching user ID:", user_data)

# 3. To create playlist, make this POST request:
conn = http.client.HTTPSConnection("api.spotify.com")
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

playlist_data = {
    "name": "JukeBot",
    "description": "Jukebox for every mood!",
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
    
# 4. Add tracks to the playlist

# First need to search for the song using the search API
TRACK_NAME = "Jukebot" 

query = urllib.parse.quote(TRACK_NAME)

# Make request to Spotify API to get the song URI
conn = http.client.HTTPSConnection("api.spotify.com")
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
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
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}
uris = [TRACK_URI]
body = json.dumps({"uris": uris})

conn.request("POST", f"/v1/playlists/{PLAYLIST_ID}/tracks", body, headers)

response = conn.getresponse()
data = json.loads(response.read().decode())

if "snapshot_id" in data:
    print("Tracks added successfully!")
else:
    print("Error adding tracks:", data)

