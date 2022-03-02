from django.urls import path
from .views import ListPoolAprs, ListEternalFarmingsAprs, ListLimitFarmingsTvl

urlpatterns = [
    path('pools/', ListPoolAprs.as_view(), name='get_pools_apr'),
    path('eternalFarmings/', ListEternalFarmingsAprs.as_view(), name='get_eternal_farmings_apr'),
    path('limitFarmings/', ListLimitFarmingsTvl.as_view(), name='get_limit_farmings_tvl'),
]
