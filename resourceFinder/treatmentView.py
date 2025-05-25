from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from resourceFinder.medical_ai.appointmentModel import Appointment
from resourceFinder.medical_ai.treatmentModel import Treatment
from resourceFinder.medical_ai.patientModel import Patient

@csrf_exempt
def create_treatment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Get the appointment
            appointment = Appointment.objects.get(id=data['appointment_id'])

            # Get the doctor from appointment or request
            doctor = appointment.doctor or request.user

            # Get the patient
            patient = Patient.objects(user=appointment.user).first()
            if not patient:
                return JsonResponse({"error": "Patient record not found for this user"}, status=400)

            # Create and save the treatment
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

            # Add treatment to patient.treatments
            patient.treatments.append(treatment)

            # Optionally update ongoing treatments
            if treatment.diagnosis and treatment.diagnosis not in patient.ongoing_treatments:
                patient.ongoing_treatments.append(treatment.diagnosis)

            patient.save()

            return JsonResponse({"message": "Treatment created and linked to patient successfully."})

        except Appointment.DoesNotExist:
            return JsonResponse({"error": "Appointment not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid HTTP method"}, status=405)
