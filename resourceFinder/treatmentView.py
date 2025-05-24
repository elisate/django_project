from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mongoengine.errors import DoesNotExist

from resourceFinder.medical_ai.appointmentModel import Appointment
from resourceFinder.medical_ai.patientModel import Patient
from resourceFinder.medical_ai.treatmentMondel import Treatment

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_treatment(request):
    try:
        data = request.data
        appointment = Appointment.objects.get(id=data["appointment_id"])

        if appointment.doctor.id != request.user.id:
            return Response({"error": "Unauthorized: not assigned to this doctor."}, status=403)

        # Avoid duplicate treatment
        if Treatment.objects(appointment=appointment).first():
            return Response({"error": "Treatment already recorded."}, status=400)

        treatment = Treatment.objects.create(
            doctor=request.user,
            appointment=appointment,
            symptoms=data["symptoms"],
            diagnosis=data["diagnosis"],
            prescription=data.get("prescription", ""),
            notes=data.get("notes", "")
        )

        # Mark appointment as completed
        appointment.status = "completed"
        appointment.save()

        # Update patient ongoing treatments
        patient = Patient.objects.get(user=appointment.user)
        patient.ongoing_treatments.append(data["diagnosis"])
        patient.save()

        return Response({"message": "Treatment saved successfully."}, status=200)

    except DoesNotExist:
        return Response({"error": "Appointment or patient not found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
