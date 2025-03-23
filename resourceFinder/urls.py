from django.urls import path
from .views import recommend 
from .patientRegister import register_user

urlpatterns = [
    path("/resourceFinder",recommend),
    path("/register",register_user)
]
