import datetime
import json
import os

from Crypto.Hash import HMAC, SHA256
from peewee import CharField, BigIntegerField

from database.models.base import BaseModel


def get_unique_hash():
    return HMAC.new(bytes(str(datetime.datetime.now()), "utf-8"), digestmod=SHA256).hexdigest()


class FileMeta(BaseModel):
    path = CharField(null=False)
    filename = CharField(default=get_unique_hash, null=False)
    extension = CharField(null=False)
    size = BigIntegerField(null=False)

    def get_full_path(self):
        return os.path.join(str(self.path), self.filename + "." + self.extension)

    def json(self):
        return json.dumps({
            "file_id": self.filename,
            "extension": self.extension,
            "size": self.size,
        })
