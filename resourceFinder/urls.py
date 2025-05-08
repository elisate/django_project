from django.urls import path
from .views import patient_predict
from .patientRegister import register_user
from .patientLogin import login_user
from .Pridiction_Res_view import get_prediction_result
from resourceFinder.hospitalView import (
    create_hospital
)
from resourceFinder.doctorView import create_doctor
from resourceFinder.patientView import create_patient
from resourceFinder.hospital_schedule_view import create_or_update_hospital_schedule
from resourceFinder.appointment_view import request_hospital_appointment

urlpatterns = [
    path("/resourceFinder",patient_predict),
    path("/register",register_user),
    path("/login",login_user),
    path("/liveResultPredicted",get_prediction_result),
    
    path("/hospitals/create",create_hospital),
    path("/doctor/create",create_doctor),
    path("/patient/create",create_patient),
    path("/schedule/create",create_or_update_hospital_schedule),
    path("/Appointment/createRequest",request_hospital_appointment)
    
    
]


