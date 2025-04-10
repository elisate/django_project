from django.urls import path
from .views import patient_predict
from .patientRegister import register_user
from .patientLogin import login_user

urlpatterns = [
    path("/resourceFinder",patient_predict),
    path("/register",register_user),
    path("/login",login_user)
]
