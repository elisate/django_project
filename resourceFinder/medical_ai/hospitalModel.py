from mongoengine import Document, StringField, ListField, ReferenceField, EmailField
from resourceFinder.medical_ai.userModel import User
from resourceFinder.medical_ai.doctorModel import Doctor

class Hospital(Document):
    user = ReferenceField(User, required=True, unique=True)  # The User who owns/manages this hospital
    hospital_name = StringField(required=True, unique=True)  # Hospital name (must be unique)
    location = StringField(required=True)  # E.g., "Kigali"
    contact = StringField()  # Optional phone number or other contact info
    email = EmailField()  # Use EmailField for validation
    Medical_Supplies = ListField(StringField())  # E.g., ["Oxygen Cylinders", "Syringes"]
    Medical_Resources = ListField(StringField())  # E.g., ["Emergency Services", "Surgery"]
    doctors_assigned = ListField(ReferenceField(Doctor))  # Doctors working at this hospital

    meta = {
        'collection': 'hospitals',  # Optional: specify collection name
        'ordering': ['hospital_name']  # Default sorting
    }

    def __str__(self):
        return self.hospital_name

    def get_doctor_names(self):
        """Return a list of full names of assigned doctors."""
        return [f"{doc.user.firstname} {doc.user.lastname}" for doc in self.doctors_assigned if doc.user]
