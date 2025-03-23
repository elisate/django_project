from django.http import JsonResponse
from resourceFinder.medical_ai.model import predict_diagnosis  # Import the AI model logic
from resourceFinder.medical_ai.models import Patient  # Import the Patient model
from resourceFinder.medical_ai.userModel import User  # Import the User model
import json
import pandas as pd
from django.views.decorators.csrf import csrf_exempt

# Load the dataset (same as in the AI model code)
file_path = 'resourceFinder/medical_ai/healthcare_data.csv'  # Correct file path for the CSV
data = pd.read_csv(file_path)

@csrf_exempt
def recommend(request):
    if request.method == "POST":
        data_request = json.loads(request.body)  # Parse incoming JSON data

        # Collect data from the request
        user_id = data_request.get('user_id')  # Get user_id from request
        symptoms = data_request.get('symptoms')
        location = data_request.get('location')

        # Validate required fields
        if not user_id or not symptoms or not location:
            return JsonResponse({"error": "User ID, Symptoms, and location are required"}, status=400)

        # Use the AI model to predict the diagnosis based on the symptoms
        predicted_diagnosis = predict_diagnosis(symptoms)

        # Fetch recommendations from the dataset based on the predicted diagnosis
        recommended_hospitals = get_recommended_hospitals(predicted_diagnosis)
        recommended_doctors = get_recommended_doctors(predicted_diagnosis)
        medical_supplies = get_medical_supplies(predicted_diagnosis)
        medical_resources = get_medical_resources(predicted_diagnosis)

        # Check if the user exists in the database
        user = User.objects(id=user_id).first()

        if not user:
            return JsonResponse({"error": "User not found"}, status=404)

        # Check if the patient already exists for this user
        patient = Patient.objects(user=user).first()

        if patient:
            # If the patient exists, update the patient data
            patient.diagnosis = predicted_diagnosis
            patient.recommended_hospitals = recommended_hospitals
            patient.recommended_doctors = recommended_doctors
            patient.medical_supplies = medical_supplies
            patient.medical_resources = medical_resources
            patient.save()
        else:
            # If the patient does not exist, create a new patient record
            patient = Patient(
                user=user,  # Associate the patient with the user
                symptoms=symptoms,
                location=location,
                diagnosis=predicted_diagnosis,
                recommended_hospitals=recommended_hospitals,
                recommended_doctors=recommended_doctors,
                medical_supplies=medical_supplies,
                medical_resources=medical_resources
            )
            patient.save()

        # Send the response back with patient data (including user association)
        response = {
            "patient_id": str(patient.id),  # MongoDB auto-generated id
            "user_id": str(user.id),  # The user id associated with the patient
            "predicted_diagnosis": predicted_diagnosis,
            "recommended_hospitals": recommended_hospitals,
            "recommended_doctors": recommended_doctors,
            "medical_supplies": medical_supplies,
            "medical_resources": medical_resources
        }
        return JsonResponse(response)

    return JsonResponse({"error": "Invalid request"}, status=400)


# Helper functions to fetch recommendations from the dataset
def get_recommended_hospitals(diagnosis):
    # Get recommended hospitals based on diagnosis
    hospitals = data[data['Diagnosis'] == diagnosis]['Recommended_Hospitals'].values
    return list(hospitals)

def get_recommended_doctors(diagnosis):
    # Get recommended doctors based on diagnosis
    doctors = data[data['Diagnosis'] == diagnosis]['Recommended_Doctors'].values
    return list(doctors)

def get_medical_supplies(diagnosis):
    # Get medical supplies based on diagnosis
    supplies = data[data['Diagnosis'] == diagnosis]['Medical_Supplies'].values
    return list(supplies)

def get_medical_resources(diagnosis):
    # Get medical resources based on diagnosis
    resources = data[data['Diagnosis'] == diagnosis]['Medical_Resources'].values
    return list(resources)
