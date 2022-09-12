from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("groups", views.GroupViewSet, basename="groups")
router.register(
    "has_permissions", views.HasPermissionViewSet, basename="has_permission"
)
router.register("rlcs", views.RlcViewSet)
router.register("permissions", views.PermissionViewSet)
router.register("notes", views.NoteViewSet)
