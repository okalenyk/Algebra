from django.db import models

from base.models import AbstractBaseModel
from contracts.models import PoolContract


class Position(AbstractBaseModel):
    last_inner_fee_growth_token_0 = models.CharField(max_length=80, blank=False, null=False)
    last_inner_fee_growth_token_1 = models.CharField(max_length=80, blank=False, null=False)
    liquidity = models.CharField(max_length=80)
    nft_id = models.CharField(max_length=16, blank=False, null=False, unique=True)
    pool = models.ForeignKey(PoolContract, on_delete=models.CASCADE, blank=False, null=True)

