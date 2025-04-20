from peewee import ForeignKeyField

from database.models.base import BaseModel
from database.models.users import AppUser


class Subscriptions(BaseModel):
    author = ForeignKeyField(AppUser, backref="subscribers_rel", null=False)
    follower = ForeignKeyField(AppUser, backref="following_rel", null=False)
