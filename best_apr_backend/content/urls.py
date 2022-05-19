from django.urls import path
from .views import ListEvents, ListPublications

urlpatterns = [
    path('events/', ListEvents.as_view(), name='get_events'),
    path('publications/', ListPublications.as_view(), name='get_publications'),
]
