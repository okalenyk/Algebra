from django.core.exceptions import ValidationError
from django.db import models

from base.models import AbstractBaseModel


class Event(AbstractBaseModel):
    KINDS = (
        ('L_FARM', 'Limit Farming'),
        ('I_FARM', 'Infinite Farming'),
        ('T_FARM', 'Tier Farming'),
        ('DROP', 'Air Drop'),
        ('COMP', 'Competition'),
        ('GIVE', 'Giveaway'),
        ('OTHER', 'Other')
    )

    title = models.CharField(max_length=64, verbose_name='Title')
    start_date = models.DateTimeField(verbose_name='Start date')
    entry_date = models.DateTimeField(null=True, blank=True, verbose_name='Entry date')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='End date')
    liquidity_limit = models.BigIntegerField(null=True, blank=True, verbose_name='Liquidity limit')
    kind = models.CharField(max_length=64, choices=KINDS, verbose_name='Kind')
    level1_lock = models.IntegerField(null=True, blank=True, verbose_name='Required for level 1')
    level1_bonus = models.IntegerField(null=True, blank=True, verbose_name='Level 1 bonus')
    level2_lock = models.IntegerField(null=True, blank=True, verbose_name='Required for level 2')
    level2_bonus = models.IntegerField(null=True, blank=True, verbose_name='Level 2 bonus')
    level3_lock = models.IntegerField(null=True, blank=True, verbose_name='Required for level 3')
    level3_bonus = models.IntegerField(null=True, blank=True, verbose_name='Level 3 bonus')
    locked_token = models.CharField(null=True, blank=True, max_length=42, verbose_name='Address of locked token')
    app_link = models.URLField(null=True, blank=True, verbose_name='App link')
    article_link = models.URLField(null=True, blank=True, verbose_name='Article link')
    image = models.ImageField(null=True, blank=True, verbose_name='Image', upload_to='events/')
    token_image = models.ImageField(null=True, blank=True, verbose_name='Token image', upload_to='events/tokens/')
    description = models.CharField(max_length=512, null=True, blank=True, verbose_name='Description')

    def clean_fields(self, exclude=None):
        errors = {}
        if self.kind == 'T_FARM':
            if self.level1_lock is None:
                errors['level1_lock'] = ['Must set required amount for level 1 for tier farming',]
            if self.level1_bonus is None:
                errors['level1_bonus'] = ['Must set bonus for level 1 for tier farming',]
            if self.level2_lock is None:
                errors['level2_lock'] = ['Must set required amount for level 2 for tier farming',]
            if self.level2_bonus is None:
                errors['level2_bonus'] = ['Must set bonus for level 2 for tier farming',]
            if self.level3_lock is None:
                errors['level3_lock'] = ['Must set required amount for level 3 for tier farming',]
            if self.level3_bonus is None:
                errors['level3_bonus'] = ['Must set bonus for level 3 for tier farming',]
            if self.locked_token is None:
                errors['locked_token'] = ['Must set locked token for tier farming', ]
        if errors != {}:
            raise ValidationError(errors)




class Publication(AbstractBaseModel):
    title = models.CharField(max_length=64, verbose_name='Title')
    description = models.CharField(max_length=512, null=True, blank=True, verbose_name='Description')
    image = models.ImageField(null=True, blank=True, verbose_name='Image', upload_to='publications/')
    link = models.URLField(null=True, blank=True, verbose_name='Link')
