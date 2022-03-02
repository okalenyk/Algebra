from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Pool, EternalFarming, LimitFarming
from logging import debug


# Create your views here.

class ListPoolAprs(APIView):
    def get(self, request, format=None):
        result = {}

        try:
            network_name = request.GET['network']
        except KeyError:
            network_name = 'Polygon'

        for pool in Pool.objects.filter(network__title=network_name):
            result[pool.address] = pool.last_apr
        return Response(result)


class ListEternalFarmingsAprs(APIView):
    def get(self, request, format=None):
        result = {}

        try:
            network_name = request.GET['network']
        except KeyError:
            network_name = 'Polygon'

        for farming in EternalFarming.objects.filter(network__title=network_name):
            result[farming.hash] = farming.last_apr
        return Response(result)


class ListLimitFarmingsTvl(APIView):
    def get(self, request, format=None):
        result = {}

        try:
            network_name = request.GET['network']
        except KeyError:
            network_name = 'Polygon'

        for farming in LimitFarming.objects.filter(network__title=network_name):
            result[farming.hash] = farming.matic_amount
        return Response(result)
