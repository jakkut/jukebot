#!/usr/bin/env python3

/* 
FireBase free tier
 -Free Authentication with limited users
 -1 GB stored data
 -50,000 reads, 50,000 writes and 50,000 deletes per day
 -Hosting: 10 GB storage and 360 MB data transfer per day
 -Cloud Functions: 2 million invocations per month
*/

/* FROM FIREBASE CONSOLE WEBPAGE

// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  secret
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

*/

// much below is example code from online that i need to debug and integrate with our code once we decide to implement this content (post update)

/* in client index.js

import firebaseConfig from './config.js';

firebase.initializeApp(firebaseConfig);

// Check if the user is logged in or in guest mode
let currentUser = null;
let isGuest = false;

// Handle login form submission
document.getElementById('login-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  firebase.auth().signInWithEmailAndPassword(email, password)
    .then((userCredential) => {
      currentUser = userCredential.user;
      isGuest = false;
      alert('Logged in successfully!');
      // Redirect or update UI
      window.location.href = '/dashboard';
    })
    .catch((error) => {
      console.error('Login failed:', error.message);
      alert('Login failed: ' + error.message);
    });
});

// Handle guest mode
document.getElementById('guest-button').addEventListener('click', () => {
  currentUser = null;
  isGuest = true;
  alert('You are now in guest mode. Your data will not be saved.');
  // Redirect or update UI
  window.location.href = '/dashboard';
});

// Save chat history 
function saveChatHistory(chatData) {
  if (isGuest) {
    // Save to local storage
    localStorage.setItem('guestChatHistory', JSON.stringify(chatData));
  } else if (currentUser) {
    // Save to Firestore
    db.collection('users').doc(currentUser.uid).update({
      chatHistory: firestore.FieldValue.arrayUnion(chatData)
    });
  }
}

// Load chat history 
function loadChatHistory() {
  if (isGuest) {
    // Load from local storage
    const chatHistory = JSON.parse(localStorage.getItem('guestChatHistory')) || [];
    return chatHistory;
  } else if (currentUser) {
    // Load from Firestore
    return db.collection('users').doc(currentUser.uid).get()
      .then((doc) => doc.data().chatHistory || []);
  }
  return [];
}

*/

/* this would be python flask in a file within the server folder

from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('server/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Middleware to verify Firebase ID token
def verify_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except:
        return None

# Registration endpoint
@app.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    password = request.json.get('password')

    try:
        user = auth.create_user(email=email, password=password)
        
        # Store user data in Firestore
        user_data = {
            "email": email,
            "playlists": [],
            "chatHistory": []
        }
        db.collection('users').document(user.uid).set(user_data)

        return jsonify({"message": "User created", "uid": user.uid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    id_token = request.json.get('idToken')

    user = verify_token(id_token)
    if not user:
        return jsonify({"error": "Invalid token"}), 401

    return jsonify({"message": f"Welcome, {user['email']}"}), 200

# Save chat history endpoint
@app.route('/save-chat', methods=['POST'])
def save_chat():
    id_token = request.headers.get('Authorization')
    chat_data = request.json.get('chatData')

    if id_token:
        # Authenticated user
        user = verify_token(id_token)
        if not user:
            return jsonify({"error": "Invalid token"}), 401

        db.collection('users').doc(user['uid']).update({
            "chatHistory": firestore.ArrayUnion([chat_data])
        })
    else:
        # Guest user (data is not saved permanently)
        pass

    return jsonify({"message": "Chat saved"}), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(port=3000)
*/