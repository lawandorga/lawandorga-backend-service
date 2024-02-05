from django.urls import include, path

from core.upload import api

urlpatterns = [
    path("query/", include(api.query_router.urls)),
]
