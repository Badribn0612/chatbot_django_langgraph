from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
from chatbot import get_chatbot_response
import traceback

def chat_interface(request):
    """Serve the chat interface"""
    return render(request, 'index.html')

def serialize_message(msg):
    """Convert LangChain message objects to serializable dictionaries"""
    if hasattr(msg, 'content') and hasattr(msg, '__class__'):
        # Handle LangChain message objects
        message_data = {
            "type": msg.__class__.__name__,
            "content": msg.content,
            "role": getattr(msg, 'role', None),
            "name": getattr(msg, 'name', None),
            "additional_kwargs": getattr(msg, 'additional_kwargs', {})
        }
        
        # Handle ToolMessage specifically
        if msg.__class__.__name__ == "ToolMessage":
            message_data.update({
                "tool_calls": getattr(msg, 'tool_calls', None),
                "tool_call_id": getattr(msg, 'tool_call_id', None),
                "tool_name": getattr(msg, 'tool_name', None),
                "tool_input": getattr(msg, 'tool_input', None),
                "tool_output": getattr(msg, 'tool_output', None)
            })
        
        # Handle AIMessage with tool calls
        elif msg.__class__.__name__ == "AIMessage":
            tool_calls = getattr(msg, 'tool_calls', None)
            if tool_calls:
                message_data["tool_calls"] = tool_calls
        
        return message_data
    elif isinstance(msg, dict):
        # Already a dictionary, return as-is
        return msg
    else:
        # Fallback for other types
        return {"content": str(msg), "type": type(msg).__name__}

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            messages = data.get("messages", [])
            user_query = data.get("query", "")
            messages.append({"role": "user", "content": user_query})
            response = get_chatbot_response(messages)
            # Serialize the messages before returning
            serialized_messages = [serialize_message(msg) for msg in response["messages"]]
            return JsonResponse({"messages": serialized_messages})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "POST request required"}, status=400)