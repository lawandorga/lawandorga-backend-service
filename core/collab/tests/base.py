from django.conf import settings
from rest_framework.test import APIRequestFactory

from core.models import (
    CollabDocument,
    HasPermission,
    Org,
    Permission,
    RlcUser,
    TextDocumentVersion,
    UserProfile,
)
from core.static import PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS


class BaseCollab:
    def setUp(self):
        self.factory = APIRequestFactory()
        self.rlc = Org.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(
            email="dummy@law-orga.de", name="Dummy 1"
        )
        self.user.set_password(settings.DUMMY_USER_PASSWORD)
        self.user.save()
        self.rlc_user = RlcUser.objects.create(
            user=self.user, email_confirmed=True, accepted=True, org=self.rlc
        )
        # keys
        self.private_key_user = self.user.get_private_key(
            password_user=settings.DUMMY_USER_PASSWORD
        )
        self.aes_key_rlc = self.rlc.get_aes_key(
            user=self.user, private_key_user=self.private_key_user
        )
        # permissions
        permission = Permission.objects.get(name=PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS)
        HasPermission.objects.create(user=self.rlc_user, permission=permission)

    def create_user(self, email, name):
        user = UserProfile.objects.create(email=email, name=name)
        user.set_password("pass1234")
        user.save()
        RlcUser.objects.create(
            user=user,
            accepted=True,
            locked=False,
            email_confirmed=True,
            is_active=True,
            org=self.rlc,
        )

    def create_collab_document(self, path="/Document"):
        collab_document = CollabDocument.objects.create(rlc=self.rlc, path=path)
        version = TextDocumentVersion(
            document=collab_document, quill=False, content="Document Content"
        )
        version.encrypt(aes_key_rlc=self.aes_key_rlc)
        version.save()
        return collab_document
