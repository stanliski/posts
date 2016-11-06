# -*- encoding: utf-8 -*-
from datetime import datetime

from peewee import Model, Proxy, MySQLDatabase, SqliteDatabase
from peewee import CharField, IntegerField, ForeignKeyField, BooleanField, TextField, DateTimeField
from playhouse.db_url import connect as _connect
from conf import DATABASE_URL as dburl
from conf import PER_PAGE_NUM
import re

__all__ = ["Label", "User", "Post", "LabelRelationship"]

# publish
PUBLISH_STATUS = 0
# hidden
HIDDEN_STATUS = 1
# trash
TRASH_STATUS = 2

# create a peewee database instance -- our models will use this database to
# persist information
datebase = SqliteDatabase(dburl)

class BaseModel(Model):
    """
    model definitions -- the standard "pattern" is to define a base model class
    that specifies which database to use.  then, any subclasses will automatically
    use the correct storage.
    """

    class Meta:
        database = datebase


class User(BaseModel):
    """
    User info for post system.
    """
    email = CharField(index=True, unique=True)
    fullname = CharField()
    admin = BooleanField(default=False)
    active = BooleanField(default=True)
    avatar = CharField()
    reg_date = DateTimeField(default=datetime.now())

    class Meta:
        order_by = ('-reg_date',)


class Label(BaseModel):
    """
    Label for posts.
    """
    text = CharField(index=True, unique=True)
    user = ForeignKeyField(User)
    timestamp = DateTimeField(default=datetime.now, index=True)

    class Meta:
        order_by = ('-timestamp',)

    def get_posts(self, page):
        public_posts = (Post.select().join(LabelRelationship,
                                           on=LabelRelationship.post)
                        .where(LabelRelationship.label == self)
                        .paginate(page, PER_PAGE_NUM))
        return public_posts

    def to_json(self):
        return {"text": self.text, "timestamp": self.timestamp, "user": self.user.id}


class Post(BaseModel):
    """
    Post blog content.
    """
    title = CharField(index=True, unique=True)
    content = TextField()
    timestamp = DateTimeField(default=datetime.now, index=True)
    status = IntegerField(default=PUBLISH_STATUS)
    user = ForeignKeyField(User)

    class Meta:
        order_by = ('-timestamp',)

    def html_content(self):
        """
        Generate HTML representation of the markdown-formatted blog entry,
        and also convert any media URLs into rich media objects such as video
        players or images.
        """
        return

    def get_labels(self):
        """
        Get post labels.
        :return: labels
        """
        labels = (Label.select().join(LabelRelationship,
                                      on=LabelRelationship.label).where(LabelRelationship.post == self))
        return labels

    def get_brief(self):
        """
        Get post brief.
        :return:
        """
        brief = self.content
        filters = ['*', '#', '`', '>']
        for filter in filters:
            brief = brief.replace(filter, '')
        if len(brief) > 250:
            return brief[0:250]
        else:
            return brief

    def to_json(self):
        return {"title": self.title, "content": self.content, "timestamp": self.timestamp, "status": self.status,
                "user": self.user.id, "id": self.id}


class LabelRelationship(BaseModel):
    """
    Many to many relationship between post and label.
    """
    post = ForeignKeyField(Post, related_name="labels")
    label = ForeignKeyField(Label, related_name="posts")

    class Meta:
        indexes = (
            (("post", "label"), True),
        )


if __name__ == "__main__":
    datebase.connect()
    datebase.create_tables([User, Label,
                            Post, LabelRelationship])
