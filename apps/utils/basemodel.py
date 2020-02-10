from datetime import datetime

from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    mod_date = models.DateTimeField(blank=True, null=True, auto_now=True)
    pub_date = models.DateTimeField(blank=True, null=True,
                                    auto_now_add=True, editable=False)

    class Meta:
        abstract = True
