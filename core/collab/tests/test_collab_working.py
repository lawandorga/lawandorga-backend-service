import json

from django.conf import settings
from django.test import Client, TestCase
from rest_framework.test import force_authenticate

from core.models import TextDocumentVersion
from core.views import CollabDocumentViewSet

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
        c = Client()
        c.login(email=self.user.email, password=settings.DUMMY_USER_PASSWORD)
        response = c.get("/api/collab/collab_documents/{}/".format(collab_document.pk))
        self.assertContains(response, "Document Content", status_code=200)

    def test_create(self):
        data = {"path": "/", "name": "My Document"}

        c = Client()
        c.login(email=self.user.email, password=settings.DUMMY_USER_PASSWORD)
        response = c.post(
            "/api/collab/collab_documents/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(
            1,
            TextDocumentVersion.objects.filter(
                document__pk=response.json()["id"]
            ).count(),
        )
        self.assertContains(response, "My Document", status_code=201)

    def test_update(self):
        collab_document = self.create_collab_document()
        data = {"path": "/", "name": "My Document"}
        c = Client()
        c.login(email=self.user.email, password=settings.DUMMY_USER_PASSWORD)
        response = c.patch(
            "/api/collab/collab_documents/{}/".format(collab_document.pk),
            json.dumps(data),
            content_type="application/json",
        )
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
