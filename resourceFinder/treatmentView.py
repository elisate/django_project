from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from resourceFinder.medical_ai.appointmentModel import Appointment
from resourceFinder.medical_ai.treatmentModel import Treatment
from resourceFinder.medical_ai.patientModel import Patient
from resourceFinder.medical_ai.userModel import User

@csrf_exempt
def create_treatment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # 1. Fetch appointment
            appointment = Appointment.objects.get(id=data['appointment_id'])

            # 2. Get doctor (from appointment or request)
            doctor = appointment.doctor or request.user

            # 3. Get or create patient linked to appointment.user
            patient = Patient.objects(user=appointment.user).first()
            if not patient:
                # Attempt auto-creation using user data
                user = appointment.user
                patient = Patient.objects.create(
                    user=user,
                    firstname=user.firstname,
                    lastname=user.lastname,
                    gender="Other",  # Default gender or use user.gender if available
                    phone="N/A"
                )

            # 4. Create treatment
            treatment = Treatment(
                doctor=doctor,
                patient=patient,
                appointment=appointment,
                symptoms=data.get('symptoms', ''),
                diagnosis=data['diagnosis'],
                prescription=data['prescription'],
                notes=data.get('notes', '')
            )
            treatment.save()

            # 5. Update patient's ongoing treatments (optional)
            if treatment.diagnosis and treatment.diagnosis not in patient.ongoing_treatments:
                patient.ongoing_treatments.append(treatment.diagnosis)
                patient.save()

            return JsonResponse({"message": "Treatment recorded and patient updated successfully."})

        except Appointment.DoesNotExist:
            return JsonResponse({"error": "Appointment not found."}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid HTTP method"}, status=405)
