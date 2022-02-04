from django.urls import path
from .views import ListPoolAprs, ListEternalFarmingsAprs

urlpatterns = [
    path('pools/', ListPoolAprs.as_view(), name='get_pools_apr'),
    path('eternalFarmings/', ListEternalFarmingsAprs.as_view(), name='get_eternal_farmings_apr')
]
