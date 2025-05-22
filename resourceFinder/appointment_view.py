from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from resourceFinder.medical_ai.userModel import User
from resourceFinder.medical_ai.hospitalModel import Hospital
from resourceFinder.medical_ai.scheduleModel import HospitalSchedule
from resourceFinder.medical_ai.PredictionResult_model import PredictionResult
from resourceFinder.medical_ai.appointmentModel import Appointment
from bson.objectid import ObjectId, InvalidId
from mongoengine.errors import DoesNotExist
from resourceFinder.utility.email_sender import send_email
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
@csrf_exempt
def get_appointments_by_hospital(request, hospital_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method allowed"}, status=405)

    try:
        hospital = Hospital.objects(id=hospital_id).first()
        if not hospital:
            return JsonResponse({"error": "Hospital not found"}, status=404)

        # Pagination: 5 rows per page
        page = int(request.GET.get("page", 1))
        rows_per_page = 5
        skip = (page - 1) * rows_per_page

        # Query appointments
        all_appointments = Appointment.objects(hospital=hospital).order_by("-date")
        total_appointments = all_appointments.count()
        total_pages = (total_appointments + rows_per_page - 1) // rows_per_page

        appointments = all_appointments.skip(skip).limit(rows_per_page)

        result = []
        for appointment in appointments:
            user = appointment.user
            prediction = PredictionResult.objects(user=user).order_by("-created_at").first()

            result.append({
                "appointment_id": str(appointment.id),
                "firstname": getattr(user, "firstname", "N/A"),
                "lastname": getattr(user, "lastname", "N/A"),
                "national_id": getattr(user, "national_id", "N/A"),
                "email": getattr(user, "email", "N/A"),
                "phone": getattr(user, "phone", "N/A"),
                "diagnosis": getattr(prediction, "diagnosis", "Not available") if prediction else "Not available",
                "date": str(appointment.date),
                "day": appointment.day,
                "start_time": appointment.start_time,
                "end_time": appointment.end_time,
                "status": appointment.status
            })

        return JsonResponse({
            "appointments": result,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_appointments": total_appointments,
                "rows_per_page": rows_per_page
            }
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
 


@csrf_exempt
def get_appointments_by_user_id(request, user_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method is allowed"}, status=405)

    try:
        # Validate user_id format
        try:
            user_object_id = ObjectId(user_id)
        except InvalidId:
            return JsonResponse({"error": "Invalid user ID format"}, status=400)

        # Pagination parameters from query params
        try:
            page = int(request.GET.get("page", 1))
            if page < 1:
                page = 1
        except ValueError:
            page = 1

        page_size = 5  # fixed page size

        # Calculate skip count
        skip = (page - 1) * page_size

        # Query total count for pagination info
        total_appointments = Appointment.objects(user=user_object_id).count()

        # Query appointments with skip and limit for pagination
        appointments = (
            Appointment.objects(user=user_object_id)
            .order_by("-date")
            .skip(skip)
            .limit(page_size)
        )

        result = []
        for appointment in appointments:
            hospital_name = "Unknown Hospital"
            try:
                if appointment.hospital:
                    hospital_name = appointment.hospital.hospital_name
            except Exception:
                pass

            result.append({
                "appointment_id": str(appointment.id),
                "hospital_name": hospital_name,
                "day": appointment.day,
                "date": str(appointment.date),
                "start_time": appointment.start_time,
                "end_time": appointment.end_time,
                "status": appointment.status,
                "created_at": appointment.created_at.isoformat(),
                "prediction_id": str(appointment.prediction.id) if appointment.prediction else "N/A",
                "user_id": str(user_object_id),
            })

        return JsonResponse({
            "appointments": result,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_appointments": total_appointments,
                "total_pages": (total_appointments + page_size - 1) // page_size,
            }
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)
    


@csrf_exempt
def get_all_pending_appointments_by_hospital(request, hospital_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method allowed"}, status=405)

    try:
        hospital = Hospital.objects(id=hospital_id).first()
        if not hospital:
            return JsonResponse({"error": "Hospital not found"}, status=404)

        # Get all appointments with status 'pending'
        pending_appointments = Appointment.objects(
            hospital=hospital,
            status="pending"
        ).order_by("-date")

        result = []
        for appointment in pending_appointments:
            user = appointment.user
            prediction = PredictionResult.objects(user=user).order_by("-created_at").first()

            result.append({
                "appointment_id": str(appointment.id),
                "firstname": getattr(user, "firstname", "N/A"),
                "lastname": getattr(user, "lastname", "N/A"),
                "national_id": getattr(user, "national_id", "N/A"),
                "email": getattr(user, "email", "N/A"),
                "phone": getattr(user, "phone", "N/A"),
                "diagnosis": getattr(prediction, "diagnosis", "Not available") if prediction else "Not available",
                "date": str(appointment.date),
                "day": appointment.day,
                "start_time": appointment.start_time,
                "end_time": appointment.end_time,
                "status": appointment.status
            })

        return JsonResponse({"appointments": result}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@csrf_exempt
def get_appointment_by_id(request, appointment_id):
    if request.method == 'GET':
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            return JsonResponse({
                "id": str(appointment.id),
                "user": str(appointment.user.id),
                "hospital": appointment.hospital.name,
                "prediction": str(appointment.prediction.id),
                "day": appointment.day,
                "date": appointment.date.strftime("%Y-%m-%d"),
                "start_time": appointment.start_time,
                "end_time": appointment.end_time,
                "status": appointment.status,
                "created_at": appointment.created_at.isoformat(),
            }, status=200)
        except DoesNotExist:
            return JsonResponse({"error": "Appointment not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def update_appointment_status(request, appointment_id):
    if request.method == 'PUT':
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            new_status = body.get('status', '').lower()

            valid_statuses = ["pending", "approved", "rejected", "completed"]
            if new_status not in valid_statuses:
                return JsonResponse({"error": f"Invalid status. Must be one of {valid_statuses}"}, status=400)

            appointment = Appointment.objects.get(id=appointment_id)
            appointment.status = new_status
            appointment.save()

            # Extract appointment data for email
            user = appointment.user
            hospital = appointment.hospital

            user_email = user.email
            subject = "Your Appointment Status Has Been Updated"

            message = f"""
            <div style="font-family: Arial, sans-serif; color: #333;">
              <div style="background-color: #3B82F6; padding: 20px; color: white; text-align: center;">
                <h1 style="margin: 0;">Appointment Status Update</h1>
              </div>

              <div style="padding: 20px;">
                <p>Dear <strong>{user.firstname} {user.lastname}</strong>,</p>

                <p>
                  We want to inform you that your appointment at <strong>{hospital.hospital_name}</strong> 
                  on <strong>{appointment.date} ({appointment.day})</strong> from 
                  <strong>{appointment.start_time}</strong> to <strong>{appointment.end_time}</strong> has been updated.
                </p>

                <p>
                  <strong>New Status:</strong> 
                  <span style="color: #3B82F6; font-weight: bold;">{new_status.capitalize()}</span>
                </p>

                <p>
                  If you have any questions or concerns, feel free to contact us. 
                  Thank you for choosing our service.
                </p>

                <p style="margin-top: 30px;">Best regards,<br><strong>MediConnect AI-RWA-CST Team</strong></p>
              </div>

              <div style="background-color: #f3f4f6; padding: 10px; text-align: center; font-size: 12px; color: #888;">
                © 2025 MediConnect AI-RWA-CST. All rights reserved.
              </div>
            </div>
            """

            send_email(to_email=user_email, subject=subject, message=message)

            return JsonResponse({
                "message": f"Appointment status updated to {new_status}",
                "appointment_id": str(appointment.id),
                "status": appointment.status
            }, status=200)

        except DoesNotExist:
            return JsonResponse({"error": "Appointment not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)