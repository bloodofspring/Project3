from peewee import CharField, ForeignKeyField, DateTimeField

from database.models.base import BaseModel
from database.models.file_meta import FileMeta


class UserProfile(BaseModel):
    first_name = CharField(max_length=32, null=False)
    last_name = CharField(max_length=32, null=True, default=None)
    about = CharField(max_length=255, null=True, default=None)
    status = CharField(max_length=255, null=True, default=None)
    profile_photo = ForeignKeyField(FileMeta, backref="profile_photos", null=True, default=None)
    profile_picture = ForeignKeyField(FileMeta, backref="profile_pictures", null=True, default=None)
    birth_date = DateTimeField(null=True, default=None)

class AppUser(BaseModel):
    email = CharField(null=False, max_length=128)
    login = CharField(null=False, max_length=32)
    password = CharField(null=False)  # password hash
    profile_data = ForeignKeyField(UserProfile, backref="user", null=False)
