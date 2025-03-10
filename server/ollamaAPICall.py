from ollama import chat
from flask import Flask, request, jsonify, render_template, session

app = Flask(__name__, static_folder='../client/static', template_folder='../client/templates')
app.secret_key = "your_secret_key"  # Needed to store session data

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_songs", methods=["POST"])
def generate_songs():
    # Get user input from the frontend
    user_input = request.json.get("content")

    # Retrieve message history from session (or initialize if empty)
    if "messages" not in session:
        session["messages"] = []
        # Only add the system prompt to the first message
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
    session.pop("messages", None)  # Clear the conversation history
    return jsonify({"message": "Conversation history cleared!"})

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8000)
