from django.contrib.admin import ModelAdmin, register


# Register your models here.
from .models import Pool, EternalFarming


@register(Pool)
class PoolAdmin(ModelAdmin):
    fields = (
        'title',
        'address',
        'last_apr'
    )
    list_display = (
        'title',
        'address',
        'last_apr'
    )
    search_fields = (
        '=address',
    )
    ordering = (
        '-last_apr',
    )
    sortable_by = (
        'last_apr',
    )
    empty_value_display = '-empty-'

@register(EternalFarming)
class EternalFarmingAdmin(ModelAdmin):
    fields = (
        'hash',
        'matic_amount',
        'last_apr'
    )
    list_display = (
        'hash',
        'matic_amount',
        'last_apr'
    )
    search_fields = (
        '=hash',
    )
    ordering = (
        '-last_apr',
    )
    sortable_by = (
        'last_apr',
    )
    empty_value_display = '-empty-'
