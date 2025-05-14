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

        if not hospital_name or not appointment_datetime_str:
            return JsonResponse({"error": "hospital_name and appointment_date are required"}, status=400)

        # 3. Fetch models
        user = User.objects(id=user_id).first()
        hospital = Hospital.objects(hospital_name=hospital_name).first()
        prediction = PredictionResult.objects(user=user).order_by("-created_at").first()

        if not all([user, hospital, prediction]):
            return JsonResponse({"error": "Missing user, hospital, or prediction"}, status=404)

        # 4. Parse datetime and extract day/time
        appointment_dt = datetime.fromisoformat(appointment_datetime_str)
        day_name = appointment_dt.strftime("%A").lower()  # "monday"
        time_str = appointment_dt.strftime("%H:%M")        # "14:58"

        # 5. Validate hospital schedule
        schedule = HospitalSchedule.objects(hospital=hospital).first()
        if not schedule:
            return JsonResponse({"error": "Hospital schedule not found"}, status=404)

        available_slots = getattr(schedule, day_name, [])
        end_time = None
        for slot in available_slots:
            start, end = slot.split("-")
            if start <= time_str <= end:
                end_time = end
                break

        if not end_time:
            return JsonResponse({"error": "Selected time not in hospital's available schedule"}, status=400)

        # 6. Create and save appointment
        appointment = Appointment(
            user=user,
            hospital=hospital,
            prediction=prediction,
            day=day_name,
            date=appointment_dt.date(),
            start_time=time_str,
            end_time=end_time,
            status="pending"  # default
        )
        appointment.save()

        # 7. Response
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
