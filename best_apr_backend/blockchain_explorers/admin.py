from django.contrib.admin import ModelAdmin, register
from django.contrib.admin.decorators import action

from .models import (
    EtherscanLikeBlockchainExplorer,
    RequestToEtherscanLikeAPI,
)


# Register your models here.
@register(EtherscanLikeBlockchainExplorer)
class EtherscanLikeBlockchainExplorerModelAdmin(ModelAdmin):
    fields = (
        'title',
        'url_endpoint',
        'api_key',
        'network',
        '_is_displayed',
    )
    list_display = (
        'id',
        'title',
        'network',
        'url_endpoint',
        'api_key',
        '_created_at',
        '_updated_at',
        '_is_displayed',
    )
    list_filter = (
        '_created_at',
        '_updated_at',
        '_is_displayed',
    )
    search_fields = (
        '=id',
        'title',
    )
    ordering = (
        '-_created_at',
    )
    empty_value_display = '-empty-'


@register(RequestToEtherscanLikeAPI)
class RequestToEtherscanLikeAPIModelAdmin(ModelAdmin):
    action = (
        'toggle_is_displayed_action',
    )
    fields = (
        'blockchain_explorer',
        'address',
        'from_block',
        'to_block',
        'response',
        '_is_displayed',
    )
    readonly_fields = (
        'blockchain_explorer',
        'address',
        'from_block',
        'to_block',
        'response',
    )
    list_display = (
        'id',
        'blockchain_explorer',
        'address',
        'from_block',
        'to_block',
        '_created_at',
        '_updated_at',
        '_is_displayed',
    )
    list_filter = (
        'address',
        '_created_at',
        '_updated_at',
        '_is_displayed',
    )
    search_fields = (
        '=id',
        'blockchain_explorer__id',
        'blockchain_explorer__title',
        'address',
        'from_block',
        'to_block',
    )
    ordering = (
        '-_created_at',
    )
    empty_value_display = '-empty-'

    def toggle_is_displayed_action(self, request, queryset):
        queryset.update(_is_dispalyed=False)
