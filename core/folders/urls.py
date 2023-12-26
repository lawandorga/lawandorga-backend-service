from django.urls import include, path

from core.folders.api import query_router

urlpatterns = [
    path("query/", include(query_router.urls)),
]
