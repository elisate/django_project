from django.http import JsonResponse
from resourceFinder.medical_ai.userModel import User  # Import User model
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password  # Import for password hashing

@csrf_exempt
def register_user(request):
    if request.method == "POST":
        # Parse the incoming JSON data
        data_request = json.loads(request.body)

        # Extract data from the request
        username = data_request.get('username')
        email = data_request.get('email')
        password = data_request.get('password')

        # Check if all fields are provided
        if not username or not email or not password:
            return JsonResponse({"error": "Missing required fields (username, email, password)"}, status=400)

        # Check if the user already exists by email or username
        existing_user = User.objects(username=username).first() or User.objects(email=email).first()

        if existing_user:
            return JsonResponse({"error": "User already exists with this username or email"}, status=400)

        # Hash the password before saving
        hashed_password = make_password(password)

        # Create a new User object with the hashed password
        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )
        new_user.save()

        # Return the user details as response (excluding password)
        response = {
            "user_id": str(new_user.id),
            "username": new_user.username,
            "email": new_user.email
        }

        return JsonResponse(response, status=201)

    # Return an error if the request method is not POST
    return JsonResponse({"error": "Invalid request method"}, status=400)
