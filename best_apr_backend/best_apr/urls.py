from django.urls import path
from .views import ListPoolAprs

urlpatterns = [
    path('pools/', ListPoolAprs.as_view(), name='get_pools_apr'),
]
