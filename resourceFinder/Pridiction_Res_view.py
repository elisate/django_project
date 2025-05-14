from django.http import JsonResponse
from resourceFinder.medical_ai.PredictionResult_model import PredictionResult
from resourceFinder.medical_ai.userModel import User

def get_prediction_result(request):
    if request.method == "GET":
        try:
            # Middleware must have added this
            user_id = getattr(request, "user_id", None)

            if not user_id:
                return JsonResponse({"error": "Unauthorized. No user ID found in request."}, status=401)

            # Find user by ID
            user = User.objects(id=user_id).first()
            if not user:
                return JsonResponse({"error": "User not found"}, status=404)

            # Fetch latest prediction for the user
            prediction = PredictionResult.objects(user=user).order_by("-created_at").first()

            if prediction:
                # Convert prediction to dict, then inject the prediction ID
                prediction_data = prediction.to_dict() if hasattr(prediction, "to_dict") else prediction.to_mongo().to_dict()
                prediction_data["prediction_id"] = str(prediction.id)  # Add the ID as 'prediction_id'
                
                return JsonResponse(prediction_data, status=200)
            else:
                return JsonResponse({"error": "No prediction found for this user"}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method. Only GET allowed."}, status=405)


def get_prediction_by_id(request, prediction_id):
    if request.method == "GET":
        try:
            # Look up the prediction by ID
            prediction = PredictionResult.objects(id=prediction_id).first()

            if not prediction:
                return JsonResponse({"error": "Prediction not found"}, status=404)

            # Convert to dict and include the ID
            prediction_data = prediction.to_dict() if hasattr(prediction, "to_dict") else prediction.to_mongo().to_dict()
            prediction_data["prediction_id"] = str(prediction.id)

            return JsonResponse(prediction_data, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method. Only GET allowed."}, status=405)