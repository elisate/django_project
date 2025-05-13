from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from resourceFinder.medical_ai.scheduleModel import HospitalSchedule, TimeSlot
from resourceFinder.medical_ai.hospitalModel import Hospital
import json

def parse_timeslots(day_data):
    if not isinstance(day_data, list):
        raise ValueError("Each day's schedule must be a list of timeslot dictionaries.")
    return [TimeSlot(**slot) for slot in day_data if isinstance(slot, dict)]


def create_or_update_hospital_schedule(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            hospital_id = data.get('hospital_id')
            hospital = Hospital.objects(id=hospital_id).first()

            if not hospital:
                return JsonResponse({"error": "Hospital not found"}, status=404)

            schedule = HospitalSchedule.objects(hospital=hospital).first()
            timeslot_fields = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

            parsed_data = {day: parse_timeslots(data.get(day, [])) for day in timeslot_fields}

            if schedule:
                for day, slots in parsed_data.items():
                    setattr(schedule, day, slots)
                schedule.save()
                return JsonResponse({"message": "Schedule updated"}, status=200)
            else:
                new_schedule = HospitalSchedule(hospital=hospital, **parsed_data)
                new_schedule.save()
                return JsonResponse({"message": "Schedule created"}, status=201)

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

def get_hospital_schedule(request, hospital_id):
    if request.method == 'GET':
        try:
            hospital = Hospital.objects(id=hospital_id).first()

            if not hospital:
                return JsonResponse({"error": "Hospital not found"}, status=404)

            schedule = HospitalSchedule.objects(hospital=hospital).first()

            if not schedule:
                return JsonResponse({"error": "Schedule not found"}, status=404)

            return JsonResponse({
                "hospital_id": str(hospital.id),
                "schedule": {
                    "monday": [slot.to_mongo().to_dict() for slot in schedule.monday],
                    "tuesday": [slot.to_mongo().to_dict() for slot in schedule.tuesday],
                    "wednesday": [slot.to_mongo().to_dict() for slot in schedule.wednesday],
                    "thursday": [slot.to_mongo().to_dict() for slot in schedule.thursday],
                    "friday": [slot.to_mongo().to_dict() for slot in schedule.friday],
                    "saturday": [slot.to_mongo().to_dict() for slot in schedule.saturday],
                    "sunday": [slot.to_mongo().to_dict() for slot in schedule.sunday],
                }
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def update_schedule_slot(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            hospital_id = data.get("hospital_id")
            day = data.get("day")
            new_slot = data.get("slot")  # The slot to add or update
            slot_index = data.get("index", None)  # Optional: index of slot to replace

            if not (hospital_id and day and new_slot):
                return JsonResponse({"error": "Missing data"}, status=400)

            hospital = Hospital.objects(id=hospital_id).first()
            if not hospital:
                return JsonResponse({"error": "Hospital not found"}, status=404)

            schedule = HospitalSchedule.objects(hospital=hospital).first()
            if not schedule:
                return JsonResponse({"error": "Schedule not found"}, status=404)

            if day not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                return JsonResponse({"error": "Invalid day name"}, status=400)

            day_slots = getattr(schedule, day)

            if slot_index is not None and isinstance(slot_index, int):
                if 0 <= slot_index < len(day_slots):
                    day_slots[slot_index] = TimeSlot(**new_slot)
                else:
                    return JsonResponse({"error": "Invalid slot index"}, status=400)
            else:
                # Append new slot if index is not provided
                day_slots.append(TimeSlot(**new_slot))

            setattr(schedule, day, day_slots)
            schedule.save()

            return JsonResponse({"message": f"{day.capitalize()} slot updated successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            hospital_id = data.get("hospital_id")
            day = data.get("day")  # e.g., "monday"
            slots = data.get("slots", [])

            if not (hospital_id and day and isinstance(slots, list)):
                return JsonResponse({"error": "Invalid input format"}, status=400)

            hospital = Hospital.objects(id=hospital_id).first()
            if not hospital:
                return JsonResponse({"error": "Hospital not found"}, status=404)

            schedule = HospitalSchedule.objects(hospital=hospital).first()
            if not schedule:
                return JsonResponse({"error": "Schedule not found"}, status=404)

            # Validate day
            valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            if day not in valid_days:
                return JsonResponse({"error": "Invalid day"}, status=400)

            # Update only the specified day
            timeslot_objs = [TimeSlot(**slot) for slot in slots if isinstance(slot, dict)]
            setattr(schedule, day, timeslot_objs)
            schedule.save()

            return JsonResponse({"message": f"{day.capitalize()} schedule updated"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)