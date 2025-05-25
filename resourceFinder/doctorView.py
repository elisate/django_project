from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.conf import settings
from datetime import datetime
import jwt
from bson.objectid import ObjectId

from resourceFinder.medical_ai.userModel import User, UserRole
from resourceFinder.medical_ai.doctorModel import Doctor
from resourceFinder.medical_ai.hospitalModel import Hospital

from resourceFinder.utility.cloudinary_helper import upload_image_to_cloudinary  # import your helper
from resourceFinder.utility.jwt_utils import  generate_jwt_token

@csrf_exempt
def create_doctor(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        data = request.POST
        image = request.FILES.get('profile_image')

        # Validate required fields
        required_fields = ['firstname', 'lastname', 'email', 'password', 'specialty']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if User.objects(email__iexact=email).first():
            return JsonResponse({'error': 'User already exists with this email'}, status=400)

        hashed_password = make_password(password)

        user = User(
            firstname=data.get('firstname'),
            lastname=data.get('lastname'),
            email=email,
            password=hashed_password,
            userRole=UserRole.DOCTOR.value
        )
        user.save()

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

        # Upload to Cloudinary and store URL
        if image:
            doctor.profile_image_url = upload_image_to_cloudinary(image)

        hospital_id = data.get('hospital_id')
        if hospital_id:
            hospital = Hospital.objects(id=hospital_id).first()
            if not hospital:
                return JsonResponse({'error': 'Hospital not found'}, status=404)

            doctor.hospital = hospital
            doctor.save()

            hospital.doctors_assigned.append(doctor)
            hospital.save()
        else:
            doctor.save()

        token = generate_jwt_token(user),

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
            'doctor_id': str(doctor.id),
            'profile_image_url': doctor.profile_image_url
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_doctors_by_hospital(request, hospital_id):
    try:
        if not ObjectId.is_valid(hospital_id):
            return JsonResponse({'error': 'Invalid hospital ID'}, status=400)

        doctors = Doctor.objects(hospital=ObjectId(hospital_id))

        doctor_list = []
        for doctor in doctors:
            doctor_list.append({
                'doctor_id': str(doctor.id),
                'firstname': doctor.user.firstname if doctor.user else "",
                'lastname': doctor.user.lastname if doctor.user else "",
                'full_name': doctor.full_name,
                'age': doctor.age,
                'gender': doctor.gender,
                'phone': doctor.phone,
                'email': doctor.email,
                'notes': doctor.notes,
                'specialty': doctor.specialty,
                'certifications': doctor.certifications,
                'available_times': doctor.available_times,
                'profile_image_url': doctor.profile_image_url or ""
            })

        return JsonResponse({'doctors': doctor_list}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
def get_doctor_by_id(request, doctor_id):
    try:
        if request.method != 'GET':
            return JsonResponse({'error': 'Only GET method is allowed'}, status=405)

        if not ObjectId.is_valid(doctor_id):
            return JsonResponse({'error': 'Invalid doctor ID'}, status=400)

        doctor = Doctor.objects(id=ObjectId(doctor_id)).first()
        if not doctor:
            return JsonResponse({'error': 'Doctor not found'}, status=404)

        return JsonResponse({
            'doctor_id': str(doctor.id),
            'firstname': doctor.user.firstname if doctor.user else "",
            'lastname': doctor.user.lastname if doctor.user else "",
            'full_name': doctor.full_name,
            'age': doctor.age,
            'gender': doctor.gender,
            'phone': doctor.phone,
            'email': doctor.email,
            'notes': doctor.notes,
            'specialty': doctor.specialty,
            'certifications': doctor.certifications,
            'available_times': doctor.available_times,
            'profile_image_url': doctor.profile_image_url or ""
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

