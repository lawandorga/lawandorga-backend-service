from django.urls import include, path

from . import api

urlpatterns = [
    path("records/", include(api.records_router.urls)),
]
