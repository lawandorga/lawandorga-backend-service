from django.urls import include, path

from . import api

urlpatterns = [path("", include(api.events_router.urls))]
