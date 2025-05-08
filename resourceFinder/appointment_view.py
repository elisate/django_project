from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from resourceFinder.medical_ai.userModel import User
from resourceFinder.medical_ai.hospitalModel import Hospital
from resourceFinder.medical_ai.scheduleModel import HospitalSchedule
from resourceFinder.medical_ai.PredictionResult_model import PredictionResult
from resourceFinder.medical_ai.appointmentModel import Appointment

@csrf_exempt
def request_hospital_appointment(request):
    if request.method == "POST":
        try:
            # Get user_id from request
            user_id = getattr(request, "user_id", None)
            if not user_id:
                return JsonResponse({"error": "Unauthorized"}, status=401)

            # Get request data
            data = json.loads(request.body)
            hospital_name = data.get("hospital_name")  # Use hospital name
            appointment_date_str = data.get("appointment_date")

            # Fetch user and hospital by name
            user = User.objects(id=user_id).first()
            hospital = Hospital.objects(hospital_name=hospital_name).first()  # Search by name
            prediction = PredictionResult.objects(user=user).order_by("-created_at").first()

            if not all([user, hospital, prediction]):
                return JsonResponse({"error": "Missing user, hospital, or prediction"}, status=400)

            # Fetch the hospital's schedule
            schedule = HospitalSchedule.objects(hospital=hospital).first()
            if not schedule:
                return JsonResponse({"error": "Hospital schedule not found"}, status=400)

            # Parse the appointment date
            appointment_dt = datetime.fromisoformat(appointment_date_str)
            weekday = appointment_dt.strftime("%A").lower()  # Get day of the week
            hour_min = appointment_dt.strftime("%H:%M")  # Get the time in HH:MM format

            # Check if the chosen time is available in the schedule
            available_slots = getattr(schedule, weekday, [])
            valid = any(start <= hour_min <= end for slot in available_slots for start, end in [slot.split("-")])

            if not valid:
                return JsonResponse({"error": "Appointment time not in hospital schedule"}, status=400)

            # Create the appointment
            appointment = Appointment(
                user=user,
                hospital=hospital,
                prediction=prediction,
                appointment_date=appointment_dt
            )
            appointment.save()

            return JsonResponse({"message": "Appointment booked", "appointment_id": str(appointment.id)})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST allowed"}, status=405)
