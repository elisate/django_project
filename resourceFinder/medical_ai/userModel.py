from mongoengine import Document, StringField
from enum import Enum

# Define Enum for user roles
class UserRole(str, Enum):
    GENERAL_USER = "general_user"
    PATIENT = "patient"
    DOCTOR = "doctor"
    HOSPITAL = "hospital"

class User(Document):
    firstname = StringField(required=True)
    lastname = StringField(required=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    userRole = StringField(
        choices=[role.value for role in UserRole],
        default=UserRole.GENERAL_USER.value
    )

    # Lazy import of Patient when it's actually needed
    def get_patient(self):
        from resourceFinder.medical_ai.models import Patient  # Lazy import to avoid circular import
        return Patient.objects(user=self).first()
