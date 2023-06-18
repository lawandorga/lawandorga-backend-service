from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api

router = DefaultRouter()


urlpatterns = [
    path("", include(router.urls)),
    path("org/", include(api.org_router.urls)),
    path("groups/", include(api.group_router.urls)),
    path("query/", include(api.query_router.urls)),
    path("notes/", include(api.note_router.urls)),
]
