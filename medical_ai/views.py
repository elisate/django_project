import joblib
import numpy as np
from django.http import JsonResponse
from rest_framework.decorators import api_view

# Load AI model
model = joblib.load("medical_ai/ai_model/model.pkl")

@api_view(['POST'])
def predict(request):
    symptoms = request.data.get("symptoms", [])
    
    if not symptoms:
        return JsonResponse({"error": "No symptoms provided"}, status=400)

    # Convert symptoms to model format (assumes dataset format)
    symptom_vector = np.zeros(len(model.feature_names_in_))
    for symptom in symptoms:
        if symptom in model.feature_names_in_:
            index = np.where(model.feature_names_in_ == symptom)[0][0]
            symptom_vector[index] = 1

    predicted_disease = model.predict([symptom_vector])[0]

    return JsonResponse({"predicted_disease": predicted_disease})
