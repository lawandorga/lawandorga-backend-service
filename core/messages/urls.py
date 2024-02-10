from django.urls import include, path

from core.messages import api

urlpatterns = [
    path("query/", include(api.query_router.urls)),
]
