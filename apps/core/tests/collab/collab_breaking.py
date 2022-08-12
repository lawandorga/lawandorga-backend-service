from django.test import TestCase
from rest_framework.test import force_authenticate

from apps.core.models import CollabDocument
from apps.core.views import CollabDocumentViewSet

from .collab_working import BaseCollab


###
# CollabDocument
###
class CollabDocumentViewSetWorking(BaseCollab, TestCase):
    def setUp(self):
        super().setUp()

    def get_doc(self, doc):
        return CollabDocument.objects.get(pk=doc.pk)

    def test_rename_works(self):
        doc1 = self.create_collab_document("/Document 1")
        doc2 = self.create_collab_document("/Document 1/Document 1.1")
        self.create_collab_document("/Document 1/Document 1.1/Document 1.1.1")
        doc4 = self.create_collab_document("/Document 1/Document 1.1/Document 1.1.2")
        self.create_collab_document("/Document 2")
        doc5 = self.create_collab_document("/Document 2/Document 2.1")
        doc2.change_name_and_save("Document X")
        self.assertEqual(self.get_doc(doc1).path, "/Document 1")
        self.assertEqual(self.get_doc(doc2).path, "/Document 1/Document X")
        self.assertEqual(
            self.get_doc(doc4).path, "/Document 1/Document X/Document 1.1.2"
        )
        self.assertEqual(self.get_doc(doc5).path, "/Document 2/Document 2.1")

    def test_name_does_not_allow_slash(self):
        collab_document = self.create_collab_document()
        view = CollabDocumentViewSet.as_view(actions={"patch": "partial_update"})
        data = {"path": "/", "name": "My$$/&.Document/Test"}
        request = self.factory.patch("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=collab_document.pk)
        self.assertContains(response, "My.DocumentTest", status_code=200)
        collab_document = self.create_collab_document("/MyDocumentTest/Document 2")
        view = CollabDocumentViewSet.as_view(actions={"patch": "partial_update"})
        data = {"path": "/", "name": "Document/#$%%#/400"}
        request = self.factory.patch("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=collab_document.pk)
        self.assertContains(response, "/MyDocumentTest/Document400", status_code=200)
