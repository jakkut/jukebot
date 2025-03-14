from ollama import chat
from flask import Flask, request, jsonify, render_template, session, make_response
from flask_sqlalchemy import SQLAlchemy
import json, os
import logging
#logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='../client/static', template_folder='../client/templates')
app.secret_key = "your_secret_key"  # Needed to store session data
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "messages.db")}'
db = SQLAlchemy(app)

class UserHistory(db.Model):
    __tablename__ = 'user_history'
    id = db.Column(db.String(64), primary_key=True)
    messages = db.Column(db.Text)

with app.app_context():
    print("Creating tables...")
    db.create_all()
    print("Tables created.")



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_songs", methods=["POST"])
def generate_songs():
    # Get user input from the frontend 
    user_input = request.json.get("content")

    #check if previous user
    user_id = request.args.get("userId")
    saved_messages = None
    if user_id:
        saved_messages = UserHistory.query.get(user_id)


    # Retrieve message history from session/user (or initialize if empty)
    if "messages" not in session:
              
        if saved_messages: #if previous user
            # Deserialize the messages (convert JSON string back to a list)
            session["messages"] =  jsonify({"messages": saved_messages.messages}) 
            user_input = "Considering the general vibe and general preferences of the previous messages, " \
            "make a playlist that fits this description: " + user_input

        else: # if new user and first message
            # Only add the system prompt to the first message
            session["messages"] = []
            user_input = "Make a playlist that fits this description: " + user_input

    # Append user message
    session["messages"].append({'role': 'user', 'content': user_input})

    # Generate response using Ollama
    response = chat(model='llama3.2', messages=session["messages"])

    # Append response to message history
    session["messages"].append({'role': 'assistant', 'content': response['message']['content']})

    # Save session
    session.modified = True

    # Return the latest response only
    return jsonify({"playlist": response['message']['content']})

@app.route("/reset", methods=["POST"])
def reset():
    # Retrieve the current messages from the session
    messages = session.get("messages", [])
    # Retrieve the userId from the request body
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided."}), 400

    user_id = data.get("userId")
    if not user_id:
        return jsonify({"message": "User ID not provided."}), 400

    if messages:
        # Save messages to the database
        saved_messages = UserHistory(id=user_id, messages=json.dumps(messages))
        db.session.merge(saved_messages)  # Update or insert
        db.session.commit()

    # Clear the session messages
    session.pop("messages", None)

    return jsonify({"message": "Conversation history cleared!"})


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8000)
