from django.urls import path

from .views import debug


urlpatterns = [
    path('debug/', debug),
]
