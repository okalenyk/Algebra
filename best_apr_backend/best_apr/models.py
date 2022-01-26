from django.db import models

from base.models import AbstractBaseModel


class Position(AbstractBaseModel):
    last_inner_fee_growth_token_0 = models.IntegerField(blank=False, null=False)
    last_inner_fee_growth_token_1 = models.IntegerField(blank=False, null=False)
    liquidity = models.IntegerField()

# Create your models here.
