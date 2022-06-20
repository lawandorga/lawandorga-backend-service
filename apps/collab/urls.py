from rest_framework.routers import DefaultRouter

from apps.collab.views import CollabDocumentViewSet
from apps.collab.views.collab_permission import CollabPermissionViewSet
from apps.collab.views.permission_for_collab_document import (
    PermissionForCollabDocumentViewSet,
)

router = DefaultRouter()
router.register("collab/collab_documents", CollabDocumentViewSet)
router.register("collab/collab_permissions", CollabPermissionViewSet)
router.register("collab/document_permissions", PermissionForCollabDocumentViewSet)
