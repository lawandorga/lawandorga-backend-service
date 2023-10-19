from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api

router = DefaultRouter()

urlpatterns = [
    path("records/v2/", include(api.records_router.urls)),
    path("", include(router.urls)),
    path("query/", include(api.query_router.urls)),
    path("deletions/", include(api.deletions_router.urls)),
    path("accesses/", include(api.accesses_router.urls)),
]
