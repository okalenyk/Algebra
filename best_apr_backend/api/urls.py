from django.urls import path, include

from .views import HealthcheckAPIView


urlpatterns = [
    path('healthcheck/', HealthcheckAPIView.as_view(), name='healthcheck'),
    path('', include('best_apr.urls')),
]
