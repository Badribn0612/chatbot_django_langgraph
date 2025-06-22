import requests

url = "http://localhost:8000/api/chatbot/"
data = {"query": "Can you tell me the latest updates on the Air India crash"}
response = requests.post(url, json=data)
print(response.json())