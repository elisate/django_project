# resourceFinder/medical_ai/appointmentModel.py

from mongoengine import Document, ReferenceField, DateTimeField, StringField, DateField
from resourceFinder.medical_ai.userModel import User
from resourceFinder.medical_ai.hospitalModel import Hospital
from resourceFinder.medical_ai.PredictionResult_model import PredictionResult
import datetime

class Appointment(Document):
    user = ReferenceField(User, required=True)  # Who made the appointment
    hospital = ReferenceField(Hospital, required=True)  # Where (which hospital)
    prediction = ReferenceField(PredictionResult, required=True)  # Why (based on AI diagnosis)

    day = StringField(required=True, choices=[
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    ])  # Day of the week (e.g., "monday")

    date = DateField(required=True)  # e.g., 2025-05-15
    start_time = StringField(required=True)  # e.g., "14:58"
    end_time = StringField(required=True)    # e.g., "20:59"

    status = StringField(default="pending", choices=[
        "pending", "approved", "cancelled", "completed"
    ])  # Default status is pending; can be updated later

    created_at = DateTimeField(default=datetime.datetime.utcnow)  # When the appointment was made

    def __str__(self):
        return f"Appointment for {self.user} at {self.hospital.name} on {self.date} ({self.day})"
