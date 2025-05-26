from django.http import JsonResponse

from resourceFinder.medical_ai.treatmentModel import Treatment
from resourceFinder.medical_ai.patientModel import Patient
from mongoengine.queryset.visitor import Q

def patients_and_treatments_by_doctor(request, doctor_id):
    # Step 1: Get all treatments by the doctor
    treatments = Treatment.objects(doctor=doctor_id)

    # Step 2: Group treatments by patient
    patient_map = {}
    for treatment in treatments:
        patient_id = str(treatment.patient.id)
        if patient_id not in patient_map:
            patient_map[patient_id] = {
                "patient": treatment.patient,
                "treatments": []
            }
        patient_map[patient_id]["treatments"].append(treatment)

    # Step 3: Build response
    response_data = []
    for entry in patient_map.values():
        patient = entry["patient"]
        treatment_list = entry["treatments"]

        patient_data = {
            "id": str(patient.id),
            "full_name": patient.get_full_name(),
            "age": patient.age,
            "gender": patient.gender,
            "phone": patient.phone,
            "hospital": patient.hospital.name if patient.hospital else None,
            "national_id": patient.national_id,
            "profile_image": patient.profile_image,
            "height_cm": patient.height_cm,
            "weight_kg": patient.weight_kg,
            "medical_history": patient.medical_history,
            "allergies": patient.allergies,
            "ongoing_treatments": patient.ongoing_treatments,
            "emergency_contact": patient.emergency_contact,
            "treatments": []
        }

        for treatment in treatment_list:
            patient_data["treatments"].append({
                "id": str(treatment.id),
                "appointment_id": str(treatment.appointment.id),
                "symptoms": treatment.symptoms,
                "diagnosis": treatment.diagnosis,
                "prescription": treatment.prescription,
                "notes": treatment.notes,
                "created_at": treatment.created_at.isoformat()
            })

        response_data.append(patient_data)

    return JsonResponse({"patients": response_data})
