from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from resourceFinder.medical_ai.userModel import User, UserRole
from resourceFinder.medical_ai.patientModel import Patient
from resourceFinder.medical_ai.hospitalModel import Hospital

@csrf_exempt
def create_patient(request):
    if request.method == 'POST':
        try:
            # Use request.POST for text fields and request.FILES for the uploaded file
            data = request.POST
            image = request.FILES.get('profile_image')

            # 1. Create User
            user = User(
                firstname=data.get('firstname'),
                lastname=data.get('lastname'),
                email=data.get('email'),
                password=data.get('password'),
                userRole=UserRole.PATIENT.value
            )
            user.save()

            # 2. Create Patient
            patient = Patient(
                user=user,
                national_id=data.get('national_id'),
                age=data.get('age'),
                gender=data.get('gender'),
                phone=data.get('phone'),
                height_cm=data.get('height'),
                weight_kg=data.get('weight'),
                profile_image=image  # FileField accepts uploaded file object
            )

            # 3. Assign to hospital (if provided)
            hospital_id = data.get('hospital_id')
            if hospital_id:
                hospital = Hospital.objects(id=hospital_id).first()
                if hospital:
                    patient.hospital = hospital

            patient.save()

            return JsonResponse({'message': 'Patient created successfully', 'patient_id': str(patient.id)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
