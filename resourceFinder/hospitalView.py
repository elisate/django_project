from django.http import JsonResponse
from resourceFinder.medical_ai.hospitalModel import Hospital
from resourceFinder.medical_ai.userModel import User, UserRole
import json
from mongoengine.errors import NotUniqueError, ValidationError

def create_hospital(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            hospital_name = data["hospital_name"]
            email = data["email"]
            password = data["password"]
            location = data["location"]
            contact = data.get("contact", "")
            supplies = data.get("Medical_Supplies", [])
            resources = data.get("Medical_Resources", [])

            # Create user (with role = hospital)
            user = User(
                hospitalName=hospital_name,
                email=email,
                password=password,
                userRole=UserRole.HOSPITAL.value
            )
            user.save()

            # Create hospital
            hospital = Hospital(
                user=user,
                hospital_name=hospital_name,
                location=location,
                contact=contact,
                email=email,
                Medical_Supplies=supplies,
                Medical_Resources=resources
            )
            hospital.save()

            return JsonResponse({
                "message": "Hospital and user account created successfully.",
                "user_id": str(user.id),
                "hospital_id": str(hospital.id)
            }, status=201)

        except NotUniqueError:
            return JsonResponse({"error": "Hospital name or email already exists."}, status=400)
        except KeyError as e:
            return JsonResponse({"error": f"Missing field: {str(e)}"}, status=400)
        except ValidationError as ve:
            return JsonResponse({"error": str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
