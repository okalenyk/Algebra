from rest_framework import serializers
from rest_framework.serializers import (
    ModelSerializer,
)

from .models import Event, Publication


class TimestampField(serializers.Field):
    def to_representation(self, value):
        return int(value.timestamp())


class ImageField(serializers.Field):
    def to_representation(self, value):
        if not value:
            return None

        request = self.context.get('request')
        image_url = value.url
        return request.build_absolute_uri(image_url)


class EventSerializer(ModelSerializer):
    start_date = TimestampField()
    end_date = TimestampField()
    entry_date = TimestampField()
    image = ImageField()
    token_image = ImageField()

    class Meta:
        model = Event
        fields = (
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
            'level1_lock',
            'level1_bonus',
            'level2_lock',
            'level2_bonus',
            'level3_lock',
            'level3_bonus',
            'locked_token',
        )


class PublicationsSerializer(ModelSerializer):
    class Meta:
        model = Publication
        fields = (
            'title',
            'description',
            'image',
            'link',
        )
