from django.http import JsonResponse
from rest_framework.views import APIView

from .models import Event, Publication
from .serializers import EventSerializer, PublicationsSerializer

# Create your views here.


class ListEvents(APIView):
    def get(self, request, format=None):
        serializer = EventSerializer(Event.objects.all(), many=True)

        return JsonResponse(serializer.data, safe=False)


class ListPublications(APIView):
    def get(self, request, format=None):
        serializer = PublicationsSerializer(Publication.objects.all(), many=True)

        return JsonResponse(serializer.data, safe=False)
