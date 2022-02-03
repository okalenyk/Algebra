from django.urls import path
from .views import ListPoolAprs, UpdateFarmingsTvl

urlpatterns = [
    path('pools/', ListPoolAprs.as_view(), name='get_pools_apr'),
    path('update_fatmings/', UpdateFarmingsTvl.as_view(), name='update')
]
