# resourceFinder/medical_ai/scheduleModel.py
from mongoengine import Document, ReferenceField, ListField, StringField
from resourceFinder.medical_ai.hospitalModel import Hospital

class HospitalSchedule(Document):
    hospital = ReferenceField(Hospital, required=True, unique=True)
    monday = ListField(StringField())
    tuesday = ListField(StringField())
    wednesday = ListField(StringField())
    thursday = ListField(StringField())
    friday = ListField(StringField())
    saturday = ListField(StringField())
    sunday = ListField(StringField())