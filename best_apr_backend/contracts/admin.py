from django.contrib.admin import ModelAdmin, register

from .models import TokenContract, Contract


# Register your models here.
@register(Contract)
class ContractModelAdmin(ModelAdmin):
    fields = (
        'title',
        'address',
        'network',
        'abi',
        '_is_displayed',
    )
    list_display = (
        'title',
        'address',
        'network',
        'abi',
        '_created_at',
        '_updated_at',
        '_is_displayed',
    )
    list_filter = (
        'network__title',
        '_created_at',
        '_updated_at',
        '_is_displayed',
    )
    search_fields = (
        '=id',
        'title',
        'address',
    )
    ordering = (
        '-_created_at',
    )
    empty_value_display = '-empty-'
    autocomplete_fields = (
        'network',
    )


@register(TokenContract)
class TokenContractModelAdmin(ModelAdmin):
    fields = (
        'title',
        'address',
        # 'provider',
        'network',
        'abi',
        '_is_displayed',
    )
    list_display = (
        'id',
        'title',
        'address',
        'network',
        '_created_at',
        '_updated_at',
        '_is_displayed',
    )
    list_filter = (
        'network__title',
        '_created_at',
        '_updated_at',
        '_is_displayed',
    )
    search_fields = (
        '=id',
        'title',
        'address',
    )
    ordering = (
        '-_created_at',
    )
    empty_value_display = '-empty-'
    autocomplete_fields = (
        'network',
    )

