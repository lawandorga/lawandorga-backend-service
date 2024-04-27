from django.urls import include, path

from core.collab import api

urlpatterns = [
    path("query/", include(api.query_router.urls)),
]
