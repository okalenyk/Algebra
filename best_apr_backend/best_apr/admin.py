from django.contrib.admin import ModelAdmin, register, display

# Register your models here.
from .models import Pool, EternalFarming, LimitFarming


@register(Pool)
class PoolAdmin(ModelAdmin):
    fields = (
        'title',
        'address',
        'last_apr'
    )
    list_display = (
        'title',
        'network',
        'address',
        'last_apr'
    )
    list_filter = (
        'network__title',
    )
    search_fields = (
        '=address',
    )
    ordering = (
        '-last_apr',
    )
    sortable_by = (
        'last_apr',
        'network',
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
        'network',
        'last_apr'
    )
    list_filter = (
        'network__title',
    )
    search_fields = (
        '=hash',
    )
    ordering = (
        '-last_apr',
    )
    sortable_by = (
        'last_apr',
        'network'
    )
    empty_value_display = '-empty-'


@register(LimitFarming)
class LimitFarmingAdmin(ModelAdmin):
    fields = (
        'hash',
        'matic_amount',
        'last_apr'
    )
    list_display = (
        'hash',
        'matic_amount',
        'network',
        'last_apr'
    )
    list_filter = (
        'network__title',
    )
    search_fields = (
        '=hash',
    )
    ordering = (
        '-last_apr',
    )
    sortable_by = (
        'last_apr',
        'network'
    )
    empty_value_display = '-empty-'