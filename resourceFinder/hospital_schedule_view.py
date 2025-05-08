from django.http import JsonResponse
from resourceFinder.medical_ai.scheduleModel import HospitalSchedule
from resourceFinder.medical_ai.hospitalModel import Hospital
import json

def create_or_update_hospital_schedule(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        hospital_id = data.get('hospital_id')
        hospital = Hospital.objects(id=hospital_id).first()  # Fetch hospital

        if not hospital:
            return JsonResponse({"error": "Hospital not found"}, status=404)

        # Try to fetch existing schedule or create a new one
        schedule = HospitalSchedule.objects(hospital=hospital).first()

        if schedule:
            # If schedule exists, update it
            schedule.monday = data.get('monday', [])
            schedule.tuesday = data.get('tuesday', [])
            schedule.wednesday = data.get('wednesday', [])
            schedule.thursday = data.get('thursday', [])
            schedule.friday = data.get('friday', [])
            schedule.saturday = data.get('saturday', [])
            schedule.sunday = data.get('sunday', [])
            schedule.save()
            return JsonResponse({"message": "Hospital schedule updated successfully"}, status=200)
        else:
            # If schedule doesn't exist, create a new one
            new_schedule = HospitalSchedule(
                hospital=hospital,
                monday=data.get('monday', []),
                tuesday=data.get('tuesday', []),
                wednesday=data.get('wednesday', []),
                thursday=data.get('thursday', []),
                friday=data.get('friday', []),
                saturday=data.get('saturday', []),
                sunday=data.get('sunday', [])
            )
            new_schedule.save()
            return JsonResponse({"message": "Hospital schedule created successfully"}, status=201)
