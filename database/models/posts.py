import json

from peewee import ForeignKeyField, CharField, IntegerField

from database.models.base import BaseModel
from database.models.file_meta import FileMeta
from database.models.users import AppUser


class Post(BaseModel):
    author = ForeignKeyField(AppUser, backref="posts", null=False)
    text = CharField(null=True)

    def dict(self, max_comments: int | None = None, show_max_replies: int | None = None, show_author: bool = True):
        if max_comments is None:
            max_comments = 50

        if show_max_replies is None:
            show_max_replies = 25

        return {
            "author": self.author.dict() if show_author else None,
            "text": self.text,
            "media": [m.media.dict() for m in self.media_rel],
            "comments": [c.dict(show_max_replies=show_max_replies) for c in self.comments[:max_comments]],
        }

    def json(self, max_comments: int | None = None, show_max_replies: int | None = None):
        return json.dumps(self.dict(max_comments=max_comments, show_max_replies=show_max_replies))


class PostsToMedia(BaseModel):
    post = ForeignKeyField(Post, backref="media_rel", null=False)
    media = ForeignKeyField(FileMeta, backref="post_rel", null=False)


class Comments(BaseModel):
    post = ForeignKeyField(Post, backref="comments", null=False)
    author = ForeignKeyField(AppUser, backref="comments", null=False)
    reply_to_comment = ForeignKeyField("self", backref="replies", null=True, default=None)
    text = CharField(null=False)
    likes = IntegerField(null=False)

    def dict(self, show_max_replies: int = 50):
        return {
            "author": self.author.dict(),
            "text": self.text,
            "likes": self.likes,
            "reply_to_comment": self.reply_to_comment.dict() if self.reply_to_comment else None,
            "replies": [c.dict() for c in self.replies[:show_max_replies]]
        }

    def json(self, show_max_replies: int = 50):
        return json.dumps(self.dict(show_max_replies=show_max_replies))
