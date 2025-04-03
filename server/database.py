import sqlite3
from contextlib import closing

DATABASE = 'jukebot.db'

def init_db():
    with closing(sqlite3.connect(DATABASE)) as conn:
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS guest_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            ''')

def add_user(username, password):
    with closing(sqlite3.connect(DATABASE)) as conn:
        with conn:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))

def user_exists(username):
    with closing(sqlite3.connect(DATABASE)) as conn:
        with conn:
            cursor = conn.execute('SELECT 1 FROM users WHERE username = ?', (username,))
            return cursor.fetchone() is not None

def get_user(username):
    with closing(sqlite3.connect(DATABASE)) as conn:
        with conn:
            cursor = conn.execute('SELECT username, password FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row:
                return {'username': row[0], 'password': row[1]}
            return None