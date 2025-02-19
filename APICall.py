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


from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(model='llama3.2', messages=[
  {
    'role': 'user',
    'content': 'can you give me a playlist with kendrick lamar songs and ariana grande songs and taylor swift songs. But only 5 songs total?',
  },
])
print(response['message']['content'])



