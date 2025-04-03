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








#!/usr/bin/env python3

#OPENAI (and DeepSeek)

# from openai import OpenAI
# client = OpenAI(
#   api_key=""
# )

# completion = client.chat.completions.create(
#   model="gpt-4o-mini",
#   max_tokens=50,
#   store=True,
#   messages=[
#     {"role": "user", "content": "write a haiku about ai"}
#   ]
# )
# print(completion.choices[0].message);


#HUGGINGFACE

# import requests

# # Hugging Face API URL for the model
# token = ''
# #try BERT or T5 models then finetune with music data 

# API_URL = "https://api-inference.huggingface.co/models/gpt2" 

# # Your Hugging Face API token
# headers = {
#     "Authorization": f"Bearer {token}"  # Add token here
# }

# def query(payload):
#     response = requests.post(API_URL, headers=headers, json=payload)
#     return response.json()

# input_data = {
#     "inputs": "What are three popular love songs?"  
# }

# # Call the API and print the response
# response = query(input_data)
# print(response)

#OLLAMA 
# first run: ollama pull llama3.2 in terminal 
