from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.conf import settings
from resourceFinder.medical_ai.userModel import User, UserRole
from resourceFinder.medical_ai.patientModel import Patient
from resourceFinder.medical_ai.hospitalModel import Hospital
from datetime import datetime
import jwt

@csrf_exempt
def create_patient(request):
    if request.method == 'POST':
        try:
            data = request.POST
            image = request.FILES.get('profile_image')

            email = data.get('email', '').strip().lower()
            password = data.get('password', '').strip()

            # Validate required fields
            required_fields = ['firstname', 'lastname', 'email', 'password', 'national_id']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

            # Prevent duplicate email
            if User.objects(email__iexact=email).first():
                return JsonResponse({'error': 'User already exists with this email'}, status=400)

            # Hash the password
            hashed_password = make_password(password)

            # Create User
            user = User(
                firstname=data.get('firstname'),
                lastname=data.get('lastname'),
                email=email,
                password=hashed_password,
                userRole=UserRole.PATIENT.value
            )
            user.save()

            # Create Patient
            patient = Patient(
                user=user,
                national_id=data.get('national_id'),
                age=data.get('age'),
                gender=data.get('gender'),
                phone=data.get('phone'),
                height_cm=data.get('height'),
                weight_kg=data.get('weight'),
                profile_image=image
            )

            # Optional hospital assignment
            hospital_id = data.get('hospital_id')
            if hospital_id:
                hospital = Hospital.objects(id=hospital_id).first()
                if hospital:
                    patient.hospital = hospital

            patient.save()

            # Generate JWT token
            payload = {
                "user_id": str(user.id),
                "email": user.email,
                "userRole": user.userRole,
                "exp": datetime.utcnow() + settings.JWT_ACCESS_TOKEN_LIFETIME,
                "iat": datetime.utcnow()
            }
            token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

            return JsonResponse({
                'message': 'Patient created successfully',
                'token': token,
                'user': {
                    'user_id': str(user.id),
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'email': user.email,
                    'userRole': user.userRole
                },
                'patient_id': str(patient.id)
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
