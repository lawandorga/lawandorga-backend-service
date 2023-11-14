from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.collab import api

from . import views

router = DefaultRouter()

router.register("collab_documents", views.CollabDocumentViewSet)
router.register("collab_permissions", views.CollabPermissionViewSet)
router.register("document_permissions", views.PermissionForCollabDocumentViewSet)


urlpatterns = [
    path("query/", include(api.query_router.urls)),
]
