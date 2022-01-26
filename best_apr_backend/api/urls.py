from django.urls import path, include

from .views import HealthcheckAPIView


urlpatterns = [
    path('healthcheck/', HealthcheckAPIView.as_view(), name='healthcheck'),
    path('vault-swaps/', include('vault_swaps.urls')),
]
