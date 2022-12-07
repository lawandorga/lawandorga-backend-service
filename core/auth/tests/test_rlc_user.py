from django.conf import settings
from django.test import Client, TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from core.models import HasPermission, Org, Permission, RlcUser, UserProfile
from core.static import PERMISSION_ADMIN_MANAGE_USERS
from core.views import RlcUserViewSet


class UserBase:
    def setUp(self):
        self.rlc = Org.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(
            email="dummy@law-orga.de", name="Dummy 1"
        )
        self.user.set_password(settings.DUMMY_USER_PASSWORD)
        self.user.save()
        self.rlc_user = RlcUser.objects.create(
            user=self.user, email_confirmed=True, accepted=True, org=self.rlc
        )
        self.rlc_user.generate_keys(settings.DUMMY_USER_PASSWORD)
        self.rlc_user.save()
        self.rlc.generate_keys()
        self.rlc_user = RlcUser.objects.get(pk=self.rlc_user.pk)
        self.private_key = self.rlc_user.user.get_private_key(
            password_user=settings.DUMMY_USER_PASSWORD
        )


class UserViewSetBase(UserBase):
    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()


class UserViewSetWorkingTests(UserViewSetBase, TestCase):
    def setUp(self):
        super().setUp()
        self.another_user = UserProfile.objects.create(
            email="test_new@test.de", name="Dummy 2"
        )
        self.another_user.set_password("test")
        self.another_user.save()
        self.another_rlc_user = RlcUser.objects.create(
            user=self.another_user, email_confirmed=True, accepted=True, org=self.rlc
        )
        self.another_rlc_user.generate_keys(settings.DUMMY_USER_PASSWORD)
        self.user.generate_keys_for_user(self.private_key, self.another_user)

    def create_rlc_user(self):
        return RlcUser.objects.create(
            user=self.user, email_confirmed=True, accepted=True
        )

    def create_another_rlc_user(self):
        return RlcUser.objects.create(
            user=self.another_user, email_confirmed=True, accepted=True
        )

    def test_email_confirmation_token_works(self):
        view = RlcUserViewSet.as_view(actions={"post": "activate"})
        rlc_user = self.rlc_user
        token = rlc_user.get_email_confirmation_token()
        request = self.factory.post("")
        response = view(request, pk=rlc_user.id, token=token)
        self.assertEqual(200, response.status_code)

    def test_password_forgotten_works(self):
        view = RlcUserViewSet.as_view(actions={"post": "password_reset"})
        data = {"email": "test@test.de"}
        request = self.factory.post("/api/users/password_forgotten/", data)
        response = view(request)
        self.assertNotEqual(403, response.status_code)

    def test_reset_password_works(self):
        view = RlcUserViewSet.as_view(actions={"post": "password_reset_confirm"})
        rlc_user = self.rlc_user
        data = {
            "token": rlc_user.get_password_reset_token(),
            "new_password": "test1234",
            "new_password_confirm": "test1234",
        }
        url = "/api/users/{}/password_reset_confirm/".format(rlc_user.pk)
        request = self.factory.post(url, data)
        response = view(request, pk=rlc_user.pk)
        self.assertEqual(200, response.status_code)
        rlc_user.user.check_password("test1234")
        assert RlcUser.objects.get(pk=rlc_user.pk).locked

    def test_change_password_works(self):
        view = RlcUserViewSet.as_view(actions={"post": "change_password"})
        self.user.rlc_user.decrypt(settings.DUMMY_USER_PASSWORD)
        private_key = self.user.rlc_user.get_private_key()
        data = {
            "current_password": settings.DUMMY_USER_PASSWORD,
            "new_password": "pass1234!",
            "new_password_confirm": "pass1234!",
        }
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(200, response.status_code)
        rlc_user = RlcUser.objects.get(user__pk=self.user.pk)
        user_key = rlc_user.get_decrypted_key_from_password("pass1234!")
        self.assertEqual(private_key, user_key.key.get_private_key().decode("utf-8"))

    # def test_destroy_works_on_myself(self):
    #     view = UserViewSet.as_view(actions={'delete': 'destroy'})
    #     rlc_user = self.rlc_user
    #     url = '/api/users/{}/'.format(rlc_user.pk)
    #     request = self.factory.delete(url)
    #     force_authenticate(request, rlc_user.user)
    #     response = view(request, pk=rlc_user.pk)
    #     self.assertEqual(204, response.status_code)

    def test_destroy_works(self):
        rlc_users = RlcUser.objects.count()
        user_profiles = UserProfile.objects.count()
        view = RlcUserViewSet.as_view(actions={"delete": "destroy"})
        rlc_user = self.rlc_user
        another_rlc_user = self.another_rlc_user
        rlc_user.grant(PERMISSION_ADMIN_MANAGE_USERS)
        request = self.factory.delete("")
        force_authenticate(request, rlc_user.user)
        response = view(request, pk=another_rlc_user.pk)
        self.assertEqual(204, response.status_code)
        self.assertEqual(RlcUser.objects.count(), rlc_users - 1)
        self.assertEqual(UserProfile.objects.count(), user_profiles - 1)

    def test_keys_are_generated(self):
        user = UserProfile.objects.create(email="test3@law-orga.de")
        RlcUser.objects.create(user=user, org=self.rlc)
        user = UserProfile.objects.get(email="test3@law-orga.de")
        user.rlc_user.generate_keys(settings.DUMMY_USER_PASSWORD)
        assert user.rlc_user.key is not None

    def test_unlock_works(self):
        rlc_user = self.rlc_user
        self.another_rlc_user.locked = True
        self.another_rlc_user.save()
        c = Client()
        c.login(email=rlc_user.email, password=settings.DUMMY_USER_PASSWORD)
        response = c.post("/api/profiles/{}/unlock/".format(self.another_rlc_user.pk))
        assert response.status_code == 200


class UserViewSetErrorTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.rlc = Org.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(email="test@test.de", name="Dummy 1")
        self.user.set_password("test")
        self.user.save()
        self.rlc_user = RlcUser.objects.create(
            user=self.user, email_confirmed=True, accepted=True, org=self.rlc
        )
        self.another_user = UserProfile.objects.create(
            email="test_new@test.de", name="Dummy 2"
        )
        self.another_user.set_password("test")
        self.another_user.save()
        self.another_rlc_user = RlcUser.objects.create(
            user=self.another_user, email_confirmed=True, accepted=True, org=self.rlc
        )

    def test_user_can_not_delete_someone_else(self):
        view = RlcUserViewSet.as_view(actions={"delete": "destroy"})
        url = "/api/users/{}/".format(self.another_rlc_user.pk)
        request = self.factory.delete(url)
        force_authenticate(request, self.rlc_user.user)
        response = view(request, pk=self.another_rlc_user.pk)
        self.assertNotEqual(204, response.status_code)

    def test_password_forgotten_fails_on_wrong_token(self):
        view = RlcUserViewSet.as_view(actions={"post": "password_reset_confirm"})
        self.rlc_user.send_password_reset_email()
        data = {
            "token": "ar9qt9-1606b5f4f0ee279d23863eb22c34f0b3",
            "new_password": "test1234",
            "password_confirm": "test1234",
        }
        url = "/api/users/{}/password_reset_confirm/".format(self.rlc_user.pk)
        request = self.factory.post(url, data)
        response = view(request, pk=self.rlc_user.pk)
        self.assertNotEqual(200, response.status_code)


class UserViewSetAccessTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.rlc = Org.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(email="test@test.de", name="Dummy 1")
        self.user.set_password("test")
        self.user.save()
        self.rlc_user = RlcUser.objects.create(
            pk=1, user=self.user, email_confirmed=True, accepted=True, org=self.rlc
        )

    def test_not_everytbody_can_hit_destroy(self):
        view = RlcUserViewSet.as_view(actions={"delete": "destroy"})
        request = self.factory.delete("/api/users/1/")
        response = view(request, pk=1)
        self.assertEqual(401, response.status_code)

    def test_everybody_can_hit_activate(self):
        view = RlcUserViewSet.as_view(actions={"post": "activate"})
        request = self.factory.post("/api/users/1/activate/token-123/")
        response = view(request, pk=1, token="token-123")
        self.assertNotEqual(403, response.status_code)
        self.assertNotEqual(401, response.status_code)

    def test_everybody_can_hit_password_reset(self):
        view = RlcUserViewSet.as_view(actions={"post": "password_reset"})
        request = self.factory.post("/api/users/password_reset/")
        response = view(request)
        self.assertNotEqual(403, response.status_code)
        self.assertNotEqual(401, response.status_code)

    def test_everybody_can_hit_password_reset_confirm(self):
        view = RlcUserViewSet.as_view(actions={"post": "password_reset_confirm"})
        request = self.factory.post("/api/users/1/password_reset_confirm/")
        response = view(request, pk=1)
        self.assertNotEqual(403, response.status_code)
        self.assertNotEqual(401, response.status_code)

    def test_not_everybody_can_hit_unlock(self):
        view = RlcUserViewSet.as_view(actions={"post": "unlock"})
        request = self.factory.post("/api/users/1/unlock/")
        response = view(request, pk=1)
        self.assertEqual(401, response.status_code)
