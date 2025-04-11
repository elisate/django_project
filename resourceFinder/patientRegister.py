from django.http import JsonResponse
from resourceFinder.medical_ai.userModel import User
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.conf import settings
from datetime import datetime
import jwt
from mongoengine.queryset.visitor import Q

@csrf_exempt
def register_user(request):
    if request.method == "POST":
        try:
            data_request = json.loads(request.body)

            # Normalize data
            username = data_request.get('username', '').strip()
            email = data_request.get('email', '').strip().lower()
            password = data_request.get('password', '').strip()

            if not username or not email or not password:
                return JsonResponse({"error": "Missing required fields (username, email, password)"}, status=400)

            # Normalize for matching (case-insensitive match)
            existing_user = User.objects(
                Q(username__iexact=username) | Q(email__iexact=email)
            ).first()

            if existing_user:
                return JsonResponse({"error": "User already exists with this username or email"}, status=400)

            hashed_password = make_password(password)

            new_user = User(
                username=username,
                email=email,
                password=hashed_password
            )
            new_user.save()

            payload = {
                "user_id": str(new_user.id),
                "username": new_user.username,
                "email": new_user.email,
                "exp": datetime.utcnow() + settings.JWT_ACCESS_TOKEN_LIFETIME,
                "iat": datetime.utcnow()
            }

            token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

            return JsonResponse({
                "token": token,
                "user": {
                    "user_id": str(new_user.id),
                    "username": new_user.username,
                    "email": new_user.email
                }
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
