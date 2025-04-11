from django.urls import path
from .views import patient_predict
from .patientRegister import register_user
from .patientLogin import login_user
from .Pridiction_Res_view import get_prediction_result

urlpatterns = [
    path("/resourceFinder",patient_predict),
    path("/register",register_user),
    path("/login",login_user),
    path("/liveResultPredicted",get_prediction_result)
]
