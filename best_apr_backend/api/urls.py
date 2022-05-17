from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings

from .views import HealthcheckAPIView


urlpatterns = [
    path('healthcheck/', HealthcheckAPIView.as_view(), name='healthcheck'),
    path('', include('best_apr.urls')),
    path('content/', include('content.urls')),
]
