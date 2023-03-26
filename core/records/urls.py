from django.urls import include, path

from . import api

urlpatterns = [
    path("records/", include(api.records_router.urls)),
    path("query/", include(api.query_router.urls)),
    path("settings/", include(api.settings_router.urls)),
]
