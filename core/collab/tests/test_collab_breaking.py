import json

from django.conf import settings
from django.test import Client, TestCase

from core.models import CollabDocument

from .test_collab_working import BaseCollab


###
# CollabDocument
###
class CollabDocumentViewSetBreaking(BaseCollab, TestCase):
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
        data = {"path": "/", "name": "My$$/&.Document/Test"}
        c = Client()
        c.login(email=self.user.email, password=settings.DUMMY_USER_PASSWORD)
        response = c.patch(
            "/api/collab/collab_documents/{}/".format(collab_document.pk),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertContains(response, "My.DocumentTest", status_code=200)
        collab_document = self.create_collab_document("/MyDocumentTest/Document 2")
        data = {"path": "/", "name": "Document/#$%%#/400"}
        response = c.patch(
            "/api/collab/collab_documents/{}/".format(collab_document.pk),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertContains(response, "/MyDocumentTest/Document400", status_code=200)
