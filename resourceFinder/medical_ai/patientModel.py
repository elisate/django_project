from mongoengine import Document, StringField, ListField, ReferenceField, FileField
from resourceFinder.medical_ai.userModel import User
from resourceFinder.medical_ai.hospitalModel import Hospital

class Patient(Document):
    user = ReferenceField(User, required=True, unique=True)
    national_id = StringField()
    profile_image = FileField()
    age = StringField()
    gender = StringField(choices=["Male", "Female", "Other"])
    phone = StringField()
    height_cm = StringField()
    weight_kg = StringField()
    hospital = ReferenceField(Hospital, required=False)  # Optional hospital reference

    medical_history = ListField(StringField())
    allergies = ListField(StringField())
    ongoing_treatments = ListField(StringField())
    emergency_contact = StringField()

    def get_full_name(self):
        return f"{self.user.firstname} {self.user.lastname}"
