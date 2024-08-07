from django.db import models

# Create your models here.
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth.models import User


class UserData(TimeStampedModel):
    user =  models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                )
    link = models.CharField(max_length=1000)
    ad_title = models.CharField(max_length=250, null=True, blank=True)
    reach = models.CharField(max_length=250, null=True, blank=True)
    countries = models.CharField(max_length=3000, null=True, blank=True)

