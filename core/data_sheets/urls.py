from django.urls import include, path

from . import api

urlpatterns = [
    path("data_sheets/", include(api.data_sheets_router.urls)),
    path("query/", include(api.query_router.urls)),
]
