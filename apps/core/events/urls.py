from . import api
from django.urls import include, path

urlpatterns = [
    path("events", include(api.events_router.urls))
]
