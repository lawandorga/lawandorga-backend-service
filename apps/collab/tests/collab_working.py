from rest_framework.test import APIRequestFactory, force_authenticate
from apps.collab.models import CollabDocument, TextDocumentVersion
from apps.api.fixtures import create_permissions
from apps.api.models import Rlc, UserProfile, RlcUser, HasPermission, Permission
from apps.api.static import PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS
from django.conf import settings
from django.test import TestCase


###
# General
###
from apps.collab.views import CollabDocumentViewSet


class BaseCollab:
    def setUp(self):
        self.factory = APIRequestFactory()
        self.rlc = Rlc.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(email='dummy@law-orga.de', name='Dummy 1', rlc=self.rlc)
        self.user.set_password(settings.DUMMY_USER_PASSWORD)
        self.user.save()
        self.rlc_user = RlcUser.objects.create(user=self.user, email_confirmed=True, accepted=True)
        # keys
        self.private_key_user = self.user.get_private_key(password_user=settings.DUMMY_USER_PASSWORD)
        self.aes_key_rlc = self.rlc.get_aes_key(user=self.user, private_key_user=self.private_key_user)
        # permissions
        create_permissions()
        permission = Permission.objects.get(name=PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS)
        HasPermission.objects.create(user_has_permission=self.user, permission=permission)

    def create_user(self, email, name):
        user = UserProfile.objects.create(email=email, name=name, rlc=self.rlc)
        user.set_password('pass1234')
        user.save()
        RlcUser.objects.create(user=user, accepted=True, locked=False, email_confirmed=True, is_active=True)

    def create_collab_document(self, path='/Document'):
        collab_document = CollabDocument.objects.create(rlc=self.rlc, path=path)
        version = TextDocumentVersion(document=collab_document, quill=False, content='Document Content')
        version.encrypt(aes_key_rlc=self.aes_key_rlc)
        version.save()
        return collab_document


###
# Collab
###
class CollabDocumentViewSetWorking(BaseCollab, TestCase):
    def test_list(self):
        self.create_collab_document('/Document 1')
        self.create_collab_document('/Document 1/Document 1.1')
        self.create_collab_document('/Document 2')
        view = CollabDocumentViewSet.as_view(actions={'get': 'list'})
        request = self.factory.get('')
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, 'Document 1.1', status_code=200)

    def test_retrieve(self):
        collab_document = self.create_collab_document()
        view = CollabDocumentViewSet.as_view(actions={'get': 'retrieve'})
        request = self.factory.get('')
        force_authenticate(request, self.user)
        response = view(request, pk=collab_document.pk)
        self.assertContains(response, 'Document Content', status_code=200)

    def test_create(self):
        view = CollabDocumentViewSet.as_view(actions={'post': 'create'})
        data = {
            'path': '/',
            'name': 'My Document'
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(1, TextDocumentVersion.objects.filter(document__pk=response.data['id']).count())
        self.assertContains(response, 'My Document', status_code=201)

    def test_update(self):
        collab_document = self.create_collab_document()
        view = CollabDocumentViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'path': '/',
            'name': 'My Document'
        }
        request = self.factory.patch('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=collab_document.pk)
        self.assertContains(response, 'My Document', status_code=200)

    def test_delete(self):
        collab_document = self.create_collab_document()
        view = CollabDocumentViewSet.as_view(actions={'delete': 'destroy'})
        request = self.factory.delete('')
        force_authenticate(request, self.user)
        response = view(request, pk=collab_document.pk)
        self.assertContains(response, '', status_code=204)

    def test_versions(self):
        pass

    def test_permissions(self):
        pass
