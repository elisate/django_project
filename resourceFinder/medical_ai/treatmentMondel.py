from mongoengine import Document, ReferenceField, StringField, DateTimeField
import datetime
from resourceFinder.medical_ai.userModel import User
from resourceFinder.medical_ai.appointmentModel import Appointment

class Treatment(Document):
    doctor = ReferenceField(User, required=True)
    appointment = ReferenceField(Appointment, required=True, unique=True)
    symptoms = StringField(required=True)
    diagnosis = StringField(required=True)
    prescription = StringField()
    notes = StringField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "doctor": str(self.doctor.id),
            "appointment": str(self.appointment.id),
            "symptoms": self.symptoms,
            "diagnosis": self.diagnosis,
            "prescription": self.prescription,
            "notes": self.notes,
            "created_at": self.created_at.isoformat()
        }
