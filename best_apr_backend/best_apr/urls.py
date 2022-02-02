from django.urls import path
from .views import get_profits

urlpatterns = [
    path('getProfits/', get_profits),
]
