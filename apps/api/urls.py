from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.api import views
from apps.internal.urls import router as internal_router

router = DefaultRouter()
router.registry.extend(internal_router.registry)
router.register("profiles", views.user.UserViewSet, basename='profiles')
router.register("groups", views.GroupViewSet, basename="groups")
router.register("permissions", views.PermissionViewSet, basename="permissions")
router.register("has_permission", views.HasPermissionViewSet, basename="has_permission")
router.register("rlcs", views.RlcViewSet, basename="rlcs")
router.register(
    "user_encryption_keys",
    views.UserEncryptionKeysViewSet,
    basename="user_encryption_keys",
)
router.register("users_rlc_keys", views.UsersRlcKeysViewSet, basename="users_rlc_keys")
router.register("notifications", views.NotificationViewSet)
router.register("notification_groups", views.NotificationGroupViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("has_permission_statics/", views.HasPermissionStaticsViewSet.as_view()),
]
