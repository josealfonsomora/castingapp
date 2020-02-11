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
    avatar = models.ImageField()
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    dob = models.DateField()
    email = models.EmailField()
    phone = models.CharField(max_length=255)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    PHONE_FIELD = 'phone'

    def __str__(self):
        return "{}: {} {}".format(self.user_type, self.name, self.surname)
