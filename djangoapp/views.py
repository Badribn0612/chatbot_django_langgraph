from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from chatbot import get_chatbot_response

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_query = data.get("query", "")
        response = get_chatbot_response(user_query)
        return JsonResponse({"response": response["messages"][-1].content})
    return JsonResponse({"error": "POST request required"}, status=400)

# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from chatbot import get_chatbot_response

# @csrf_exempt
# def chatbot_api(request, query):
#     # Only allow GET requests for this style
#     if request.method == "GET":
#         response = get_chatbot_response(query)
#         return JsonResponse({"response": response["messages"][-1].content})
#     return JsonResponse({"error": "GET request required"}, status=400)