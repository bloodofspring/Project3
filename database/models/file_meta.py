import random
import string

from peewee import CharField, BigIntegerField

from database.models.base import BaseModel


def generate_string():
    return "".join(random.choices(string.hexdigits + string.ascii_letters, k=32))


class FileMeta(BaseModel):
    path = CharField(null=False)
    filename = CharField(default=generate_string, null=False)
    extension = CharField(null=False)
    size = BigIntegerField(null=False)
