from django.http import JsonResponse
from rest_framework.viewsets import ModelViewSet

from .models import Event, Publication
from .serializers import EventSerializer, PublicationsSerializer
from logging import debug

# Create your views here.


class ListEvents(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get(self, request):
        serializer = self.get_serializer(self.queryset, many=True)

        return JsonResponse(serializer.data, safe=False)


class ListPublications(ModelViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationsSerializer

    def get(self, request):
        serializer = self.get_serializer(self.queryset, many=True)

        return JsonResponse(serializer.data, safe=False)
