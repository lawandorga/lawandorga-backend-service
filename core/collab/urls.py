from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("collab_documents", views.CollabDocumentViewSet)
router.register("collab_permissions", views.CollabPermissionViewSet)
router.register("document_permissions", views.PermissionForCollabDocumentViewSet)
