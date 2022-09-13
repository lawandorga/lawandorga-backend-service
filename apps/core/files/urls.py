from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("file_base", views.FileViewSet)
router.register("permission_for_folder", views.PermissionForFolderViewSet)
router.register("folder_permission", views.FolderPermissionViewSet)
router.register("folder", views.FolderViewSet)
