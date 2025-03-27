from django.urls import path
from .views import patient_predict
from .patientRegister import register_user

urlpatterns = [
    path("/resourceFinder",patient_predict),
    path("/register",register_user)
]
