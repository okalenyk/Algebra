from django.shortcuts import render
from django.http import HttpResponse
from .services.functions import update_pools_apr

# Create your views here.

def get_profits(request):
    update_pools_apr()
    return HttpResponse('kek')
