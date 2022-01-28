from django.contrib.admin import ModelAdmin, register


# Register your models here.
from .models import Position


@register(Position)
class PositionAdmin(ModelAdmin):
    fields = (
        'last_inner_fee_growth_token_0',
        'last_inner_fee_growth_token_1',
        'liquidity',
        'nft_id',
    )
    list_display = (
        'nft_id',
        'liquidity',
    )
    search_fields = (
        '=nft_id',
    )
    empty_value_display = '-empty-'
