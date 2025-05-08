from django.http import JsonResponse
from resourceFinder.medical_ai.userModel import User, UserRole
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.conf import settings
from datetime import datetime
import jwt

@csrf_exempt
def register_user(request):
    if request.method == "POST":
        try:
            data_request = json.loads(request.body)

            # Normalize data
            firstname = data_request.get('firstname', '').strip()
            lastname = data_request.get('lastname', '').strip()
            email = data_request.get('email', '').strip().lower()
            password = data_request.get('password', '').strip()
            user_role = data_request.get('userRole', UserRole.PATIENT.value)

            # Validate required fields
            if not firstname or not lastname or not email or not password:
                return JsonResponse({"error": "Missing required fields (firstname, lastname, email, password)"}, status=400)

            # Validate userRole
            if user_role not in [role.value for role in UserRole]:
                return JsonResponse({"error": "Invalid userRole"}, status=400)

            # Check for existing user by email only
            if User.objects(email__iexact=email).first():
                return JsonResponse({"error": "User already exists with this email"}, status=400)

            # Hash the password
            hashed_password = make_password(password)

            # Create and save the new user
            new_user = User(
                firstname=firstname,
                lastname=lastname,
                email=email,
                password=hashed_password,
                userRole=user_role
            )
            new_user.save()

            # Prepare JWT payload
            payload = {
                "user_id": str(new_user.id),
                "firstname": new_user.firstname,
                "lastname": new_user.lastname,
                "email": new_user.email,
                "userRole": new_user.userRole,
                "exp": datetime.utcnow() + settings.JWT_ACCESS_TOKEN_LIFETIME,
                "iat": datetime.utcnow()
            }

            token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

            return JsonResponse({
                "token": token,
                "user": {
                    "user_id": str(new_user.id),
                    "firstname": new_user.firstname,
                    "lastname": new_user.lastname,
                    "email": new_user.email,
                    "userRole": new_user.userRole
                }
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
