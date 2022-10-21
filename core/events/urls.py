from django.urls import include, path

from . import api

urlpatterns = [path("events/", include(api.events_router.urls))]
