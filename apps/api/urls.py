from apps.recordmanagement.urls import router as records_router
from rest_framework.routers import DefaultRouter
from apps.internal.urls import router as internal_router
from apps.collab.urls import router as collab_router
from apps.files.urls import router as files_router
from django.urls import path, include
from apps.api import views

router = DefaultRouter()
router.registry.extend(internal_router.registry)
router.registry.extend(collab_router.registry)
router.registry.extend(files_router.registry)
router.registry.extend(records_router.registry)
router.register("profiles", views.RlcUserViewSet, basename='profiles')
router.register("statistic_users", views.StatisticsUserViewSet)
router.register("groups", views.GroupViewSet, basename="groups")
router.register("has_permissions", views.HasPermissionViewSet, basename="has_permission")
router.register("rlcs", views.RlcViewSet)
router.register("notifications", views.NotificationViewSet)
router.register('permissions', views.PermissionViewSet)
router.register("notification_groups", views.NotificationGroupViewSet)
router.register('notes', views.NoteViewSet)
router.register('statistic', views.StatisticViewSet, basename='statistic')
router.register('rlc_statistic', views.RlcStatisticViewSet, basename='rlc_statistic')
urlpatterns = [path("", include(router.urls))]
