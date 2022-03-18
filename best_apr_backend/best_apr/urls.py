from django.urls import path
from .views import ListPoolAprs, ListEternalFarmingsAprs, ListLimitFarmingsTvl, ListLimitFarmingsAprs

urlpatterns = [
    path('pools/', ListPoolAprs.as_view(), name='get_pools_apr'),
    path('APR/eternalFarmings/', ListEternalFarmingsAprs.as_view(), name='get_eternal_farmings_apr'),
    path('APR/limitFarmings/', ListLimitFarmingsAprs.as_view(), name='get_limit_farmings_apr'),
    path('TVL/limitFarmings/', ListLimitFarmingsTvl.as_view(), name='get_limit_farmings_tvl'),
]
