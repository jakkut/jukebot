# Jukebot 🕺

EECS 449 Project
who up jukin they bot

**Adding notes in case we need instructions on how to build/run JukeBot (bc I'm def going to forget what I did to get it to work)**    
~ Make sure Ollama is installed (create virtual environment if you want, then run `pip install ollama` and `brew install ollama`)  
~ Start Ollama (`brew services start ollama`)  
~ Pull the model (`ollama pull llama3.2`)  
~ Make sure Flask is installed (`pip install Flask`)  
~ Run the Flask server (`python server/ollamaAPICall.py`)  
~ Navigate to http://localhost:8000/ in browser and you should see JukeBot  
