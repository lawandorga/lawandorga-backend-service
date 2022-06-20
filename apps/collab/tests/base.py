from django.conf import settings
from rest_framework.test import APIRequestFactory

from apps.api.fixtures import create_permissions
from apps.api.models import HasPermission, Permission, Rlc, RlcUser, UserProfile
from apps.api.static import PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS
from apps.collab.models import CollabDocument, TextDocumentVersion


class BaseCollab:
    def setUp(self):
        self.factory = APIRequestFactory()
        self.rlc = Rlc.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(
            email="dummy@law-orga.de", name="Dummy 1", rlc=self.rlc
        )
        self.user.set_password(settings.DUMMY_USER_PASSWORD)
        self.user.save()
        self.rlc_user = RlcUser.objects.create(
            user=self.user, email_confirmed=True, accepted=True
        )
        # keys
        self.private_key_user = self.user.get_private_key(
            password_user=settings.DUMMY_USER_PASSWORD
        )
        self.aes_key_rlc = self.rlc.get_aes_key(
            user=self.user, private_key_user=self.private_key_user
        )
        # permissions
        create_permissions()
        permission = Permission.objects.get(name=PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS)
        HasPermission.objects.create(
            user_has_permission=self.user, permission=permission
        )

    def create_user(self, email, name):
        user = UserProfile.objects.create(email=email, name=name, rlc=self.rlc)
        user.set_password("pass1234")
        user.save()
        RlcUser.objects.create(
            user=user, accepted=True, locked=False, email_confirmed=True, is_active=True
        )

    def create_collab_document(self, path="/Document"):
        collab_document = CollabDocument.objects.create(rlc=self.rlc, path=path)
        version = TextDocumentVersion(
            document=collab_document, quill=False, content="Document Content"
        )
        version.encrypt(aes_key_rlc=self.aes_key_rlc)
        version.save()
        return collab_document
