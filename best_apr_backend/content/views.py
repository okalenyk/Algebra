from django.http import JsonResponse
from rest_framework.views import APIView

from .models import Event, Publication
from .serializers import EventSerializer, PublicationsSerializer

# Create your views here.


class ListEvents(APIView):
    def get(self, request, format=None):
        serializer = EventSerializer(Event.objects.order_by('-_created_at'), many=True, context={"request": request})

        return JsonResponse(serializer.data, safe=False)


class ListPublications(APIView):
    def get(self, request, format=None):
        serializer = PublicationsSerializer(Publication.objects.order_by('-_created_at')[:3], many=True, context={"request": request})

        return JsonResponse(serializer.data, safe=False)
