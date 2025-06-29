# import requests

# url = "http://localhost:8000/api/chatbot/"
# data = {"query": "I want to know about the Air India Flight crash. Could you provide me some information?"}
# response = requests.post(url, json=data)
# print(response.json())

import requests

url = "http://localhost:8000/api/chatbot/"
messages = []

while True:
    user_query = input("You: ")
    if user_query == "quit":
        break
    
    # Add the user message to the conversation
    messages.append({"role": "user", "content": user_query})
    payload = {"messages": messages, "query": user_query}
    # print(f"Sending payload: {payload}")
    
    try:
        response = requests.post(url, json=payload)
        # print(f"Response status: {response.status_code}")
        # print(f"Response headers: {response.headers}")
        # print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            # Update messages with the response, but keep them in the original format
            response_messages = data["messages"]
            
            # Convert the response back to the format LangChain expects
            for msg in response_messages:
                if msg["type"] == "AIMessage":
                    messages.append({"role": "assistant", "content": msg["content"]})
                elif msg["type"] == "ToolMessage":
                    messages.append({"role": "tool", "content": msg["content"], "tool_call_id": msg.get("tool_call_id")})
                elif msg["type"] == "HumanMessage":
                    # Skip human messages as they're already in the conversation
                    continue
            
            # Print the last assistant message
            for msg in reversed(response_messages):
                if msg["type"] == "AIMessage":
                    print("Bot:", msg["content"])
                    break
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response text: {response.text}")
    except Exception as e:
        print(f"Request error: {e}")