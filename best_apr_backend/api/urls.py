from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings

from .views import HealthcheckAPIView, send_form_to_email


urlpatterns = [
    path('healthcheck/', HealthcheckAPIView.as_view(), name='healthcheck'),
    path('send_form/', send_form_to_email, name='send_email'),
    path('', include('best_apr.urls')),
    path('content/', include('content.urls')),
]
