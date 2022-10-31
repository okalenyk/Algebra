from django.db import models

from base.models import AbstractBaseModel
from networks.models import Network


class Pool(AbstractBaseModel):
    title = models.CharField(max_length=64)
    address = models.CharField(max_length=42)
    last_apr = models.FloatField(blank=True, null=True)
    network = models.ForeignKey(Network, on_delete=models.CASCADE)


class EternalFarming(AbstractBaseModel):
    hash = models.CharField(max_length=66, unique=True)
    native_amount = models.FloatField(blank=True, null=True)
    last_apr = models.FloatField(blank=True, null=True)
    network = models.ForeignKey(Network, on_delete=models.CASCADE)


class LimitFarming(AbstractBaseModel):
    hash = models.CharField(max_length=66, unique=True)
    native_amount = models.FloatField(blank=True, null=True)
    last_apr = models.FloatField(blank=True, null=True)
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
