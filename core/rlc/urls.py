from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()

router.register(
    "has_permissions", views.HasPermissionViewSet, basename="has_permission"
)
router.register("rlcs", views.RlcViewSet)
router.register("permissions", views.PermissionViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("org/", include(api.org_router.urls)),
    path("groups/", include(api.group_router.urls)),
    path("query/", include(api.query_router.urls)),
    path("notes/", include(api.note_router.urls)),
]
