from flask import Flask, render_template, request, redirect, url_for, session, flash
import database
import hashlib
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this for production!

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

if __name__ == '__main__':
    database.init_db()
    app.run(debug=True)