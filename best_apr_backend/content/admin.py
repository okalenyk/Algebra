from django.contrib.admin import ModelAdmin, register, display

# Register your models here.
from .models import Event, Publication


@register(Event)
class EventAdmin(ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': (
                'title',
                'description',
                'start_date',
                'entry_date',
                'end_date',
                'liquidity_limit',
                'kind',
                'app_link',
                'article_link',
                'image',
                'token_image',
            )
        }),
        ('Tier farming info', {
            'classes': ('collapse',),
            'fields': (
                'level1_lock',
                'level1_bonus',
                'level2_lock',
                'level2_bonus',
                'level3_lock',
                'level3_bonus',
                'locked_token',
            ),
        }),
    )
    list_display = (
        'title',
        'start_date',
        'kind',
    )
    list_filter = (
        'kind',
    )
    search_fields = (
        '=title',
    )
    ordering = (
        'start_date',
    )
    sortable_by = (
        'start_date',
    )
    empty_value_display = '-empty-'


@register(Publication)
class PublicationAdmin(ModelAdmin):
    fields = (
        'title',
        'description',
        'image',
        'link',
    )
    list_display = (
        'title',
    )
    search_fields = (
        '=title',
    )
    ordering = (
        '_created_at',
    )
    sortable_by = (
        '_created_at',
    )
    empty_value_display = '-empty-'
