from mongoengine import Document, StringField, ListField, ReferenceField
from resourceFinder.medical_ai.userModel import User
from mongoengine import FileField

class Doctor(Document):
    user = ReferenceField(User, required=True, unique=True)  # Link to User account
    full_name = StringField(required=True)
    age = StringField()
    gender = StringField(choices=["Male", "Female", "Other"])
    profile_image = FileField()
    phone = StringField()
    email = StringField()
    notes = StringField()
    
    specialty = StringField()
    certifications = ListField(StringField())
    available_times = ListField(StringField())

    hospital = ReferenceField('Hospital', required=False)  # ✅ Use string reference here

    def get_user_email(self):
        return self.user.email if self.user else None

    def get_full_name(self):
        return self.full_name
