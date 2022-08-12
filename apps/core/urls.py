from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.core import views
from apps.core.api import keys_router, rlc_user_router
from apps.recordmanagement.urls import router as records_router

router = DefaultRouter()

router.register("collab/collab_documents", views.CollabDocumentViewSet)
router.register("collab/collab_permissions", views.CollabPermissionViewSet)
router.register("collab/document_permissions", views.PermissionForCollabDocumentViewSet)

router.register("files/file_base", views.FileViewSet)
router.register("files/permission_for_folder", views.PermissionForFolderViewSet)
router.register("files/folder_permission", views.FolderPermissionViewSet)
router.register("files/folder", views.FolderViewSet)

router.register("articles", views.ArticleViewSet)
router.register("pages/index", views.IndexPageViewSet)
router.register("pages/imprint", views.ImprintPageViewSet)
router.register("pages/toms", views.TomsPageViewSet)
router.register("pages/help", views.HelpPageViewSet)
router.register("roadmap-items", views.RoadmapItemViewSet)

router.registry.extend(records_router.registry)
router.register("profiles", views.RlcUserViewSet, basename="profiles")
router.register("statistic_users", views.StatisticsUserViewSet)
router.register("groups", views.GroupViewSet, basename="groups")
router.register(
    "has_permissions", views.HasPermissionViewSet, basename="has_permission"
)
router.register("rlcs", views.RlcViewSet)
router.register("permissions", views.PermissionViewSet)
router.register("notes", views.NoteViewSet)
router.register("statistics", views.StatisticsViewSet, basename="statistic")
router.register("rlc_statistics", views.RlcStatisticsViewSet, basename="rlc_statistic")

urlpatterns = [
    path("", include(router.urls)),
    path("rlc_users/", include(rlc_user_router.urls)),
    path("keys/", include(keys_router.urls)),
]
