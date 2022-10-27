from django.conf import settings
from django.test import TestCase

from core.auth.oidc_provider_settings import userinfo
from core.models import MatrixUser, Org, RlcUser, UserProfile


class MatrixUserBase:
    def setUp(self):
        rlc = Org.objects.create(name="Test RLC")

        self.user1 = UserProfile.objects.create(email="dummy@law-orga.de", name="Dummy")
        self.user1.set_password(settings.DUMMY_USER_PASSWORD)
        self.user1.save()
        self.rlc_user1 = RlcUser.objects.create(
            user=self.user1, email_confirmed=True, accepted=True, org=rlc
        )
        self.matrix_user1 = MatrixUser.objects.create(user=self.user1)

        user2 = UserProfile.objects.create(email="tester1@law-orga.de", name="Tester1")
        user2.set_password("pass1234")
        user2.save()
        self.rlc_user2 = RlcUser.objects.create(
            user=user2, email_confirmed=True, accepted=True, org=rlc
        )
        self.matrix_user2 = MatrixUser.objects.create(
            user=user2, _group="Different group"
        )

        user3 = UserProfile.objects.create(email="tester2@law-orga.de", name="Tester2")
        user3.set_password("pass1234")
        user3.save()
        self.matrix_user3 = MatrixUser.objects.create(user=user3)


class MatrixUserTests(MatrixUserBase, TestCase):
    def test_user_groups(self):
        assert self.matrix_user1.group == "Test RLC"
        assert self.matrix_user2.group == "Different group"
        assert self.matrix_user3.group == ""


class OIDCTests(MatrixUserBase, TestCase):
    def test_userinfo(self):
        claims = userinfo({}, self.user1)
        assert claims["name"] == "Dummy"
        assert claims["email"] == "dummy@law-orga.de"
