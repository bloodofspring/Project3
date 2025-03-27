from datetime import datetime, timedelta

from peewee import ForeignKeyField, DateTimeField

from database.models.base import BaseModel
from database.models.file_meta import FileMeta
from database.models.users import AppUser


def next_day():
    return datetime.now() + timedelta(hours=24)


class Stories(BaseModel):
    author = ForeignKeyField(AppUser, backref="stories", null=False)
    content = ForeignKeyField(FileMeta, backref="stories", null=False)
    show_until = DateTimeField(default=next_day, null=False)
