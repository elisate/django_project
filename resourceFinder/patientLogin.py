from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from resourceFinder.medical_ai.userModel import User, UserRole
from resourceFinder.medical_ai.hospitalModel import Hospital
from django.conf import settings
import json
import jwt
from datetime import datetime
from resourceFinder.utility.jwt_utils import generate_jwt_token
@csrf_exempt
def login_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return JsonResponse({"error": "Email and password are required"}, status=400)

            user = User.objects(email=email).first()

            if not user or not check_password(password, user.password):
                return JsonResponse({"error": "Invalid email or password"}, status=401)

            # Prepare payload for JWT
            payload = {
                "user_id": str(user.id),
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email,
                "exp": datetime.utcnow() + settings.JWT_ACCESS_TOKEN_LIFETIME,
                "iat": datetime.utcnow()
            }

            token = generate_jwt_token(user)

            # Get hospital ID if the user is a hospital
            hospital_id = None
            if user.userRole == UserRole.HOSPITAL.value:
                hospital = Hospital.objects(user=user).first()
                if hospital:
                    hospital_id = str(hospital.id)

            return JsonResponse({
                "token": token,
                "user": {
                    "user_id": str(user.id),
                    "firstname": user.firstname,
                    "lastname": user.lastname,
                    "email": user.email,
                    "userRole": user.userRole,
                    "hospital_id": hospital_id  # include hospital ID here
                }
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
