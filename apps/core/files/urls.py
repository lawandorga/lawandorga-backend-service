from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("files/file_base", views.FileViewSet)
router.register("files/permission_for_folder", views.PermissionForFolderViewSet)
router.register("files/folder_permission", views.FolderPermissionViewSet)
router.register("files/folder", views.FolderViewSet)
