from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.conf import settings
from datetime import datetime
import jwt

from resourceFinder.medical_ai.userModel import User, UserRole
from resourceFinder.medical_ai.doctorModel import Doctor
from resourceFinder.medical_ai.hospitalModel import Hospital

@csrf_exempt
def create_doctor(request):
    if request.method == 'POST':
        try:
            data = request.POST
            image = request.FILES.get('profile_image')

            email = data.get('email', '').strip().lower()
            password = data.get('password', '').strip()

            # Required field validation
            required_fields = ['firstname', 'lastname', 'email', 'password', 'specialty']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

            # Check for duplicate email
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
                userRole=UserRole.DOCTOR.value
            )
            user.save()

            # Create Doctor
            doctor = Doctor(
                user=user,
                full_name=data.get('full_name'),
                age=data.get('age'),
                gender=data.get('gender'),
                phone=data.get('phone'),
                email=email,
                notes=data.get('notes'),
                specialty=data.get('specialty'),
                certifications=data.getlist('certifications'),
                available_times=data.getlist('available_times'),
            )

            if image:
                doctor.profile_image.put(image, content_type=image.content_type)

            # Assign to hospital if provided
            hospital_id = data.get('hospital_id')
            if hospital_id:
                hospital = Hospital.objects(id=hospital_id).first()
                if not hospital:
                    return JsonResponse({'error': 'Hospital not found'}, status=404)

                doctor.hospital = hospital
                doctor.save()

                # Add doctor to hospital's assigned list
                hospital.doctors_assigned.append(doctor)
                hospital.save()
            else:
                doctor.save()

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
                'message': 'Doctor created successfully',
                'token': token,
                'user': {
                    'user_id': str(user.id),
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'email': user.email,
                    'userRole': user.userRole
                },
                'doctor_id': str(doctor.id)
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
