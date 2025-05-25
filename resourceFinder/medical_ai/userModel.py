from mongoengine import Document, StringField
from enum import Enum

# Define Enum for user roles
class UserRole(str, Enum):
    
    PATIENT = "patient"
    DOCTOR = "doctor"
    HOSPITAL = "hospital"
    SUPER_ADMIN="superAdmin"

class User(Document):
    firstname = StringField(required=False)
    lastname = StringField(required=False)
    hospitalName = StringField(required=False)
    phone = StringField(required=False)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    userRole = StringField(
        choices=[role.value for role in UserRole],
        default=UserRole.PATIENT.value
    )

    # Lazy import of Patient when it's actually needed
    def get_patient(self):
        from resourceFinder.medical_ai.patientModel import Patient  # Lazy import to avoid circular import
        return Patient.objects(user=self).first()
