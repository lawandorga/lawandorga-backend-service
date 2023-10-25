from django.urls import include, path

from . import api

urlpatterns = [
    path("records/v2/", include(api.records_router.urls)),
    path("query/", include(api.query_router.urls)),
]
