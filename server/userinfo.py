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

