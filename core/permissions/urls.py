from django.urls import include, path

from . import api

urlpatterns = [
    path("query/", include(api.query_router.urls)),
    path("has_permissions/", include(api.has_permission_router.urls)),
]
