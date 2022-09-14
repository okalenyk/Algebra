from django.contrib.admin import register, ModelAdmin

from .models import Network


# Register your models here.
@register(Network)
class NetworkModelAdmin(ModelAdmin):
    fields = (
        'title',
        'subgraph_url',
        'subgraph_blocks_urls',
        'subgraph_farming_url',
        '_is_displayed',
    )
    list_display = (
        'id',
        'title',
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

