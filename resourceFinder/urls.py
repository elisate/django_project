from django.urls import path
from .views import patient_predict
from .patientRegister import register_user
from .patientLogin import login_user
from .Pridiction_Res_view import (get_prediction_result,get_prediction_by_id)
from resourceFinder.hospitalView import (
    create_hospital
)
from resourceFinder.doctorView import (create_doctor,get_doctors_by_hospital,get_doctor_by_id)
from resourceFinder.patientView import (create_patient,get_patients_by_hospital)
from resourceFinder.hospital_schedule_view import (create_or_update_hospital_schedule,
                                                   get_hospital_schedule,update_schedule_slot,
                                                   delete_schedule_slot,
                                                   get_hospital_schedule_by_name
                                                   )
from resourceFinder.appointment_view import (request_hospital_appointment,
                                             get_appointments_by_hospital,
                                             get_appointments_by_user_id,
                                             get_all_pending_appointments_by_hospital,
                                             update_appointment_status,
                                             get_appointment_by_id,
                                             assign_doctor_to_appointment,
                                             get_appointments_by_doctor_email)
from resourceFinder.contactView import createContact




urlpatterns = [
    #------------------AUTHENTICATION----------------------
    path("/register",register_user),
    path("/login",login_user),
    #------------------ARTIFICIAL INTELLIGENCE---------------
    path("/resourceFinder",patient_predict),
    path("/liveResultPredicted",get_prediction_result),
    path("/liveResultPredicted/predictions/<str:prediction_id>/",get_prediction_by_id),
    #----------------HOSPITAL------------------
    path("/hospitals/create",create_hospital),
    #---------------DOCTOR------------
    path("/doctor/create",create_doctor),
    path("/doctor/getDoctorById/<str:doctor_id>",get_doctor_by_id),
    path("/doctor/getDoctorByHospitalId/<str:hospital_id>",get_doctors_by_hospital),
    path("/patient/create",create_patient),
    #----------------HOSPITAL SCHEDULE---------------
    path("/schedule/create",create_or_update_hospital_schedule),
    path('/schedule/get/<str:hospital_id>/',get_hospital_schedule),
    path("/schedule/update_day",update_schedule_slot),
    path("/schedule/delete_slot",delete_schedule_slot),
    path("/schedule/getByHospitalName/<str:hospital_name>/",get_hospital_schedule_by_name),
    #--------------APPOINTMENT-------------------------
    path("/Appointment/createRequest",request_hospital_appointment),
    path("/Appointment/getAppointmentByHospId/<hospital_id>",get_appointments_by_hospital),
    path("/Appointment/getAppointmentByUserId/<str:user_id>",get_appointments_by_user_id),
    path("/Appointment/getAppointmentById/<str:appointment_id>",get_appointment_by_id),
    path("/Appointment/getPatientByHospId/<hospital_id>",get_patients_by_hospital),
    path("/appointment/getAllPendingAppointmentsByHospId/<str:hospital_id>",get_all_pending_appointments_by_hospital),
    path('/appointment/update-status/<str:appointment_id>',update_appointment_status),
    path('/appointment/assignToDoctor-status',assign_doctor_to_appointment),
    path('/appointment/by-doctor-email/<str:email>/', get_appointments_by_doctor_email),

    #---------------------------------- CONTACT-------------
    path("/contact/createContact",createContact),

    
]


