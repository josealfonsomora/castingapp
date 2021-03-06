import uuid

from django.db import models
from django.contrib.auth.models import User

from ..utils.basemodel import BaseModel


class PostMedia(BaseModel):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False,
    )
    postitem = models.ForeignKey('Post', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    datafile = models.FileField()
    media_type = models.CharField(max_length=20, default="unknown")

    def natural_key(self):
        return {'media_type': self.media_type, 'url': self.datafile.url, 'title': self.title, 'id': self.uuid}

    def __str__(self):
        return "Post {} - {} - {}. UUID: {}".format(self.postitem.id, self.media_type, self.title, self.uuid)


class Post(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    title = models.CharField(max_length=255, blank=True, null=True)
    media = models.ManyToManyField(PostMedia, null=True, blank=True)
    post_type = models.CharField(max_length=255)

    def __str__(self):
        return "{} - {}".format(self.user.profile.name, self.title)

    def to_json(self):
        return dict(
            active=self.active,
            deleted=self.deleted,
            pub_date=self.pub_date,
            mod_date=self.mod_date,
            user={'name':self.user.profile.name, 'surname':self.user.profile.surname, 'user_type':self.user.profile.user_type.natural_key()},
            text=self.text,
            title=self.title,
            post_type=self.post_type,
            media=[media.natural_key() for media in self.media.all()]
        )
