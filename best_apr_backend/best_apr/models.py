from django.db import models

from base.models import AbstractBaseModel


class Pool(AbstractBaseModel):
    title = models.CharField(max_length=64)
    address = models.CharField(max_length=42, unique=True)
    last_apr = models.FloatField(blank=True, null=True)
