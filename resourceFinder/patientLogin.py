from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from resourceFinder.medical_ai.userModel import User
import json

@csrf_exempt
def login_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Only expecting email and password
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return JsonResponse({"error": "Email and password are required"}, status=400)

            # Find the user by email
            user = User.objects(email=email).first()

            if not user or not check_password(password, user.password):
                return JsonResponse({"error": "Invalid email or password"}, status=401)

            # Successful login response
            return JsonResponse({
                "user_id": str(user.id),
                "username": user.username,
                "email": user.email
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
