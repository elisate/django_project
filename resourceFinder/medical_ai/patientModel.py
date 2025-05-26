# patientModel.py
from mongoengine import Document, StringField, ListField, ReferenceField
from resourceFinder.medical_ai.userModel import User
from resourceFinder.medical_ai.hospitalModel import Hospital

class Patient(Document):
    user = ReferenceField(User, required=True, unique=True)
    national_id = StringField()
    profile_image = StringField()
    age = StringField()
    gender = StringField(choices=["Male", "Female", "Other"])
    phone = StringField()
    height_cm = StringField()
    weight_kg = StringField()
    firstname = StringField()
    lastname = StringField()
    hospital = ReferenceField(Hospital, required=False)

    medical_history = ListField(StringField())
    allergies = ListField(StringField())
    ongoing_treatments = ListField(StringField())
    emergency_contact = StringField()

    #  Correct way to reference Treatment to avoid circular import
    treatments = ListField(ReferenceField('Treatment'))

    def get_full_name(self):
        return f"{self.user.firstname} {self.user.lastname}"
