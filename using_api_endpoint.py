import requests

url = "http://localhost:8000/api/chatbot/"
data = {"query": "Hello, chatbot!"}
response = requests.post(url, json=data)
print(response.json())