from django.db import models
from django.contrib.auth.models import User

from ..utils.basemodel import BaseModel


class UserType(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)

    def natural_key(self):
        return '{}'.format(self.name)


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    surname = models.CharField(max_length=255, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, unique=True)
    validated = models.BooleanField(default=False)
    authentication_code = models.CharField(max_length=10, null=True, blank=True)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {} {}".format(self.user_type, self.name, self.surname)
