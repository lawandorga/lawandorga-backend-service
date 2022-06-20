from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.api import views, views2
from apps.collab.urls import router as collab_router
from apps.files.urls import router as files_router
from apps.internal.urls import router as internal_router
from apps.recordmanagement.urls import router as records_router

router = DefaultRouter()
router.registry.extend(internal_router.registry)
router.registry.extend(collab_router.registry)
router.registry.extend(files_router.registry)
router.registry.extend(records_router.registry)
router.register("profiles", views.RlcUserViewSet, basename="profiles")
router.register("statistic_users", views.StatisticsUserViewSet)
router.register("groups", views.GroupViewSet, basename="groups")
router.register(
    "has_permissions", views.HasPermissionViewSet, basename="has_permission"
)
router.register("rlcs", views.RlcViewSet)
router.register("notifications", views.NotificationViewSet)
router.register("permissions", views.PermissionViewSet)
router.register("notification_groups", views.NotificationGroupViewSet)
router.register("notes", views.NoteViewSet)
router.register("statistics", views.StatisticsViewSet, basename="statistic")
router.register("rlc_statistics", views.RlcStatisticsViewSet, basename="rlc_statistic")
urlpatterns = [
    path("", include(router.urls)),
    path("keys/", views2.keys),
    path("keys/<int:id>/", views2.keys),
    path("keys/test/", views2.keys),
]
