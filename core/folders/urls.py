from django.urls import include, path

from core.folders.api import folders_router, query_router

urlpatterns = [
    path("folders/", include(folders_router.urls)),
    path("query/", include(query_router.urls)),
]
