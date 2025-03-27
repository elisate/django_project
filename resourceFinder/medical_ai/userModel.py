# userModel.py

from mongoengine import Document, StringField

class User(Document):
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)

    # Lazy import of Patient when it's actually needed
    def get_patient(self):
        from resourceFinder.medical_ai.models import Patient  # Lazy import to avoid circular import
        return Patient.objects(user=self).first()