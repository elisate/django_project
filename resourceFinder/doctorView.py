from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from resourceFinder.medical_ai.userModel import User, UserRole
from resourceFinder.medical_ai.doctorModel import Doctor
from resourceFinder.medical_ai.hospitalModel import Hospital

@csrf_exempt
def create_doctor(request):
    if request.method == 'POST':
        try:
            # Use request.POST for text and request.FILES for the file
            data = request.POST

            # 1. Create User
            user = User(
                firstname=data.get('firstname'),
                lastname=data.get('lastname'),
                email=data.get('email'),
                password=data.get('password'),
                userRole=UserRole.DOCTOR.value
            )
            user.save()

            # 2. Create Doctor
            doctor = Doctor(
                user=user,
                full_name=data.get('full_name'),
                age=data.get('age'),
                gender=data.get('gender'),
                phone=data.get('phone'),
                email=data.get('email'),
                notes=data.get('notes'),
                specialty=data.get('specialty'),
                certifications=data.getlist('certifications'),
                available_times=data.getlist('available_times'),
            )

            # 3. Handle image upload if provided
            if 'profile_image' in request.FILES:
                image = request.FILES['profile_image']
                doctor.profile_image.put(image, content_type=image.content_type)

            # 4. Assign hospital if provided
            hospital_id = data.get('hospital_id')
            if hospital_id:
                hospital = Hospital.objects(id=hospital_id).first()
                if not hospital:
                    return JsonResponse({'error': 'Hospital not found'}, status=404)
                
                doctor.hospital = hospital
                doctor.save()

                # Add doctor to hospital
                hospital.doctors_assigned.append(doctor)
                hospital.save()
            else:
                doctor.save()

            return JsonResponse({'message': 'Doctor created successfully', 'doctor_id': str(doctor.id)})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
