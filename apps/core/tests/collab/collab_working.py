from django.test import TestCase
from rest_framework.test import force_authenticate

from apps.core.models import TextDocumentVersion
from apps.core.views import CollabDocumentViewSet

from .base import BaseCollab


###
# CollabDocument
###
class CollabDocumentViewSetWorking(BaseCollab, TestCase):
    def test_list(self):
        self.create_collab_document("/Document 1")
        self.create_collab_document("/Document 1/Document 1.1")
        self.create_collab_document("/Document 2")
        view = CollabDocumentViewSet.as_view(actions={"get": "list"})
        request = self.factory.get("")
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, "Document 1.1", status_code=200)

    def test_retrieve(self):
        collab_document = self.create_collab_document()
        view = CollabDocumentViewSet.as_view(actions={"get": "retrieve"})
        request = self.factory.get("")
        force_authenticate(request, self.user)
        response = view(request, pk=collab_document.pk)
        self.assertContains(response, "Document Content", status_code=200)

    def test_create(self):
        view = CollabDocumentViewSet.as_view(actions={"post": "create"})
        data = {"path": "/", "name": "My Document"}
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(
            1,
            TextDocumentVersion.objects.filter(
                document__pk=response.data["id"]
            ).count(),
        )
        self.assertContains(response, "My Document", status_code=201)

    def test_update(self):
        collab_document = self.create_collab_document()
        view = CollabDocumentViewSet.as_view(actions={"patch": "partial_update"})
        data = {"path": "/", "name": "My Document"}
        request = self.factory.patch("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=collab_document.pk)
        self.assertContains(response, "My Document", status_code=200)

    def test_delete(self):
        collab_document = self.create_collab_document()
        view = CollabDocumentViewSet.as_view(actions={"delete": "destroy"})
        request = self.factory.delete("")
        force_authenticate(request, self.user)
        response = view(request, pk=collab_document.pk)
        self.assertContains(response, "", status_code=204)

    def test_versions(self):
        pass

    def test_permissions(self):
        pass
