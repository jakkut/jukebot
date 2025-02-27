#OLLAMA 
# first run: ollama pull llama3.2 in terminal 


from ollama import chat
from ollama import ChatResponse

messages = []

# Start the conversation with the first user input
user_input = input("You: ")
messages.append({'role': 'user', 'content': user_input})

response: ChatResponse = chat(model='llama3.2', messages=messages)
print("JukeBot:", response['message']['content'])

# Continue the conversation
while True:
    # Take user input to continue the conversation
    user_input = input("\nYou: ")
    
    # STOP WITH EXIT OR QUIT
    if user_input.lower() in ['exit', 'quit']:
        print("Ending the conversation.")
        break
    
    messages.append({'role': 'user', 'content': user_input})
    
    response = chat(model='llama3.2', messages=messages)
    
    print("JukeBot:", response['message']['content'])



