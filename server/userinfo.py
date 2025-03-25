import sqlite3

# Creates new database users                          
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create user table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username VARCHAR2(100) NOT NULL PRIMARY KEY,
        password VARCHAR2(100)
    );
               
    CREATE TABLE IF NOT EXISTS chats (
        username VARCHAR2(100) NOT NULL,
        sessionID VARCHAR2(100) NOT NULL PRIMARY KEY,
        FOREIGN KEY (username) REFERENCES users(username)
    );
''')

# # Insert into users
# cursor.execute(
#     "INSERT INTO users (username, password) VALUES (?, ?)", ([username], [password]))
#     # Somehow make [username] and [password] the input from the website
# )

# # Insert into sessionID
# cursor.execute(
#     "INSERT INTO cahts (username, sessionID) VALUES (?, ?)", ([username], [sessionID]))
#     # Somehow make [username] the input from the website and [sessionID] pulled form Ollama
# ) 

conn.commit()

conn.close()

''' Joys craziness:
import sqlite3
import uuid
import hashlib
from flask import current_app

def get_db():
    """Get database connection with Flask app context."""
    if not hasattr(current_app, 'sqlite_db'):
        current_app.sqlite_db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        current_app.sqlite_db.row_factory = sqlite3.Row
    return current_app.sqlite_db

def init_db():
    """Initialize database tables."""
    with current_app.app_context():
        db = get_db()
        db.execute(users table above)
        db.execute(chats table above)
        db.commit()

def make_hash(password):
    """Your original hash function for new passwords."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    return "$".join([algorithm, salt, password_hash])

def verify_hash(stored_hash, input_password):
    """Your original verification function."""
    parts = stored_hash.split('$')
    if len(parts) != 3:
        return False
    algorithm, salt, _ = parts
    hash_obj = hashlib.new(algorithm)
    hash_obj.update((salt + input_password).encode('utf-8'))
    return stored_hash == "$".join([algorithm, salt, hash_obj.hexdigest()])

def create_user(username, password):
    """Create new user with hashed password."""
    password_hash = make_hash(password)
    try:
        db = get_db()
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password_hash)
        )
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(username, password):
    """Verify user credentials."""
    db = get_db()
    user = db.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    return user and verify_hash(user['password'], password)
'''