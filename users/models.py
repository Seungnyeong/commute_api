from django.db import models
from core.models import TimeStampedModel
from django.contrib.auth.models import AbstractUser


# Create your models here.


class User(AbstractUser, TimeStampedModel):

    class Meta:
        db_table = "users"
        managed = True
        verbose_name_plural = "직원정보"
