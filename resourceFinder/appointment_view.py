from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from resourceFinder.medical_ai.userModel import User
from resourceFinder.medical_ai.hospitalModel import Hospital
from resourceFinder.medical_ai.scheduleModel import HospitalSchedule
from resourceFinder.medical_ai.PredictionResult_model import PredictionResult
from resourceFinder.medical_ai.appointmentModel import Appointment

@csrf_exempt
def request_hospital_appointment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        # 1. Get user ID from request
        user_id = getattr(request, "user_id", None)
        if not user_id:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        # 2. Parse request data
        data = json.loads(request.body)
        hospital_name = data.get("hospital_name")
        appointment_datetime_str = data.get("appointment_date")  # Example: "2025-05-15T14:58"
        start_time = data.get("start_time")  # Optional
        end_time = data.get("end_time")      # Optional

        if not hospital_name or not appointment_datetime_str:
            return JsonResponse({"error": "hospital_name and appointment_date are required"}, status=400)

        # 3. Fetch models
        user = User.objects(id=user_id).first()
        hospital = Hospital.objects(hospital_name=hospital_name).first()
        prediction = PredictionResult.objects(user=user).order_by("-created_at").first()

        if not all([user, hospital, prediction]):
            return JsonResponse({"error": "Missing user, hospital, or prediction"}, status=404)

        # 4. Parse datetime and fallback for times if not provided
        appointment_dt = datetime.fromisoformat(appointment_datetime_str)
        day_name = appointment_dt.strftime("%A").lower()

        if not start_time:
            start_time = appointment_dt.strftime("%H:%M")

        if not end_time:
            temp_dt = appointment_dt + timedelta(minutes=30)
            end_time = temp_dt.strftime("%H:%M")

        # 5. Create and save appointment
        appointment = Appointment(
            user=user,
            hospital=hospital,
            prediction=prediction,
            day=day_name,
            date=appointment_dt.date(),
            start_time=start_time,
            end_time=end_time,
            status="pending"
        )
        appointment.save()

        # 6. Response
        return JsonResponse({
            "message": "Appointment booked successfully",
            "appointment": {
                "id": str(appointment.id),
                "user": str(user.id),
                "hospital": hospital.hospital_name,
                "day": appointment.day,
                "date": str(appointment.date),
                "time": f"{appointment.start_time} - {appointment.end_time}",
                "status": appointment.status
            }
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
