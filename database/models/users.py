import json

from peewee import CharField, ForeignKeyField, DateTimeField, BooleanField

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
    email_is_hidden = BooleanField(default=False, null=False)
    login = CharField(null=False, max_length=32)
    password = CharField(null=False)  # password hash
    profile_data = ForeignKeyField(UserProfile, backref="user", null=False)

    def json(self):
        return json.dumps({
            "profile_data": {
                "first_name": self.profile_data.first_name,
                "about": self.profile_data.about,
                "status": self.profile_data.status,
                "birth_date": str(self.profile_data.birth_date),
                "profile_media": {
                    "profile_photo": self.profile_data.profile_photo.json() if self.profile_data.profile_photo else None,
                    "profile_picture": self.profile_data.profile_picture.json() if self.profile_data.profile_picture else None,
                }
            },
            "email": self.email if not self.email_is_hidden else None,
            "login": self.login,
        })
