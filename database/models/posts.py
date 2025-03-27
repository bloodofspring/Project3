from peewee import ForeignKeyField, CharField, IntegerField

from database.models.base import BaseModel
from database.models.file_meta import FileMeta
from database.models.users import AppUser


class Post(BaseModel):
    author = ForeignKeyField(AppUser, backref="posts", null=False)
    text = CharField(null=False)

class PostsToMedia(BaseModel):
    post = ForeignKeyField(Post, backref="media_rel", null=False)
    media = ForeignKeyField(FileMeta, backref="post_rel", null=False)

class Comments(BaseModel):
    author = ForeignKeyField(AppUser, backref="posts", null=False)
    reply_to_comment = ForeignKeyField("self", backref="replies", null=True, default=None)
    text = CharField(null=False)
    likes = IntegerField(null=False)
