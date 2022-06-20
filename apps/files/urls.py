from rest_framework.routers import DefaultRouter

from apps.files.views import *

router = DefaultRouter()
router.register("files/file_base", FileViewSet)
router.register("files/permission_for_folder", PermissionForFolderViewSet)
router.register("files/folder_permission", FolderPermissionViewSet)
router.register("files/folder", FolderViewSet)
