from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .services.functions import update_eternal_farmings_tvl
from .models import Pool


# Create your views here.

class ListPoolAprs(APIView):
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        result = {}
        for pool in Pool.objects.all():
            result[pool.address] = pool.last_apr
        return Response(result)


class UpdateFarmingsTvl(APIView):
    def get(self, request, format=None):
        update_eternal_farmings_tvl()
        return Response('success')
