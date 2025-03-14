from ollama import chat
from flask import Flask, request, jsonify, render_template, session, make_response
import json

app = Flask(__name__, static_folder='../client/static', template_folder='../client/templates')
app.secret_key = "your_secret_key"  # Needed to store session data

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_songs", methods=["POST"])
def generate_songs():
    # Get user input from the frontend if there
    user_input = request.json.get("content")
    user_id = request.cookies.get("userId")
    if user_id: 
        saved_messages = request.cookies.get(f"saved_messages_{user_id}")
       

    # Retrieve message history from session/user (or initialize if empty)
    if "messages" not in session:      
        if saved_messages: #if previous user
            # Deserialize the messages (convert JSON string back to a list)
            messages = json.loads(saved_messages)
            session["messages"] = messages  # Restore messages to the session
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

    # Retrieve the userId from the cookie
    user_id = request.cookies.get("userId")

    if user_id:
        # Save the messages to a new cookie (or server-side storage) using the userId as a key
        response = make_response(jsonify({"message": "Conversation history cleared!"}))
        response.set_cookie(
            f"saved_messages_{user_id}",  # Unique cookie name for the user
            json.dumps(messages),  # Serialize messages to JSON
            max_age=30 * 24 * 60 * 60,  # Cookie expiration (e.g., 30 days)
            path="/",  # Cookie path
            httponly=True,  # Prevent client-side JavaScript access
            secure=True  # Ensure the cookie is sent only over HTTPS
        )
    else:
        response = make_response(jsonify({"message": "User ID not found."}), 400)

    # Clear the session messages
    session.pop("messages", None)

    return response


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8000)
