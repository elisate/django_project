# resourceFinder/medical_ai/appointmentModel.py
from mongoengine import Document, ReferenceField, DateTimeField
from resourceFinder.medical_ai.userModel import User
from resourceFinder.medical_ai.hospitalModel import Hospital
from resourceFinder.medical_ai.PredictionResult_model import PredictionResult
import datetime

class Appointment(Document):
    user = ReferenceField(User, required=True)
    hospital = ReferenceField(Hospital, required=True)
    prediction = ReferenceField(PredictionResult, required=True)
    appointment_date = DateTimeField(default=datetime.datetime.utcnow)
