from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.core.models import HasPermission, Permission, Org, RlcUser, UserProfile
from apps.core.static import PERMISSION_ADMIN_MANAGE_USERS, get_all_permission_strings
from apps.core.views import RlcUserViewSet


class UserBase:
    def setUp(self):
        self.rlc = Org.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(
            email="dummy@law-orga.de", name="Dummy 1", rlc=self.rlc
        )
        self.user.set_password(settings.DUMMY_USER_PASSWORD)
        self.user.save()
        self.rlc_user = RlcUser.objects.create(
            user=self.user, email_confirmed=True, accepted=True
        )
        self.rlc.generate_keys()
        self.rlc_user = RlcUser.objects.get(pk=self.rlc_user.pk)
        self.private_key = bytes(self.rlc_user.private_key).decode("utf-8")
        self.create_permissions()

    def create_permissions(self):
        for perm in get_all_permission_strings():
            Permission.objects.create(name=perm)


class UserViewSetBase(UserBase):
    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()


class UserViewSetWorkingTests(UserViewSetBase, TestCase):
    def setUp(self):
        super().setUp()
        self.another_user = UserProfile.objects.create(
            email="test_new@test.de", name="Dummy 2", rlc=self.rlc
        )
        self.another_user.set_password("test")
        self.another_user.save()
        self.another_rlc_user = RlcUser.objects.create(
            user=self.another_user, email_confirmed=True, accepted=True
        )
        self.user.generate_keys_for_user(self.private_key, self.another_user)

    def create_rlc_user(self):
        return RlcUser.objects.create(
            user=self.user, email_confirmed=True, accepted=True
        )

    def create_another_rlc_user(self):
        return RlcUser.objects.create(
            user=self.another_user, email_confirmed=True, accepted=True
        )

    def create_permissions(self):
        for perm in get_all_permission_strings():
            Permission.objects.create(name=perm)

    def test_create_works(self):
        view = RlcUserViewSet.as_view(actions={"post": "create"})
        data = {
            "name": "Test",
            "email": "test2@test.de",
            "password": "test",
            "password_confirm": "test",
            "rlc": self.rlc.id,
        }
        request = self.factory.post("", data)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RlcUser.objects.filter(user__email="test2@test.de").exists())

    def test_email_confirmation_token_works(self):
        view = RlcUserViewSet.as_view(actions={"post": "activate"})
        rlc_user = self.rlc_user
        token = rlc_user.get_email_confirmation_token()
        request = self.factory.post("")
        response = view(request, pk=rlc_user.id, token=token)
        self.assertEqual(response.status_code, 200)

    def test_login_works(self):
        view = RlcUserViewSet.as_view(actions={"post": "login"})
        data = {
            "email": "dummy@law-orga.de",
            "password": settings.DUMMY_USER_PASSWORD,
        }
        request = self.factory.post("/api/users/login/", data)
        response = view(request)
        self.assertContains(response, "access")
        self.assertContains(response, "refresh")
        self.assertContains(response, "user")
        self.assertContains(response, "rlc")
        self.assertContains(response, "permissions")
        self.assertEqual(response.status_code, 200)

    def test_password_forgotten_works(self):
        view = RlcUserViewSet.as_view(actions={"post": "password_reset"})
        data = {"email": "test@test.de"}
        request = self.factory.post("/api/users/password_forgotten/", data)
        response = view(request)
        self.assertNotEqual(response.status_code, 403)

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
        self.assertEqual(response.status_code, 200)
        view = RlcUserViewSet.as_view(actions={"post": "login"})
        data = {
            "email": "test@test.de",
            "password": "test1234",
        }
        request = self.factory.post("/api/users/login/", data)
        response = view(request)
        # 400 response because the account is locked now to have its keys regenerated
        self.assertContains(response, "non_field_errors", status_code=400)

    def test_retrieve_works(self):
        view = RlcUserViewSet.as_view(actions={"get": "retrieve"})
        rlc_user = self.rlc_user
        url = "/api/users/{}/".format(rlc_user.pk)
        request = self.factory.get(url)
        force_authenticate(request, rlc_user.user)
        response = view(request, pk=rlc_user.pk)
        self.assertEqual(response.status_code, 200)

    def test_change_password_works(self):
        view = RlcUserViewSet.as_view(actions={"post": "change_password"})
        self.user.rlc_user.decrypt(settings.DUMMY_USER_PASSWORD)
        private_key = self.user.rlc_user.private_key
        data = {
            "current_password": settings.DUMMY_USER_PASSWORD,
            "new_password": "pass1234!",
            "new_password_confirm": "pass1234!",
        }
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        keys = RlcUser.objects.get(user__pk=self.user.pk)
        keys.decrypt("pass1234!")
        self.assertEqual(private_key, keys.private_key)

    # def test_destroy_works_on_myself(self):
    #     view = UserViewSet.as_view(actions={'delete': 'destroy'})
    #     rlc_user = self.rlc_user
    #     url = '/api/users/{}/'.format(rlc_user.pk)
    #     request = self.factory.delete(url)
    #     force_authenticate(request, rlc_user.user)
    #     response = view(request, pk=rlc_user.pk)
    #     self.assertEqual(response.status_code, 204)

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
        self.assertEqual(response.status_code, 204)
        self.assertEqual(RlcUser.objects.count(), rlc_users - 1)
        self.assertEqual(UserProfile.objects.count(), user_profiles - 1)

    def test_update_works(self):
        view = RlcUserViewSet.as_view(actions={"patch": "partial_update"})
        rlc_user = self.rlc_user
        data = {
            "phone": "3243214321",
        }
        request = self.factory.patch("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=rlc_user.pk)
        self.assertEqual(response.status_code, 200)

    def test_update_works_on_another_user(self):
        self.rlc_user.grant(PERMISSION_ADMIN_MANAGE_USERS)
        view = RlcUserViewSet.as_view(actions={"patch": "partial_update"})
        data = {"phone": "3243214321"}
        request = self.factory.patch("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.another_rlc_user.pk)
        self.assertEqual(response.status_code, 200)

    def test_keys_are_generated(self):
        user = UserProfile.objects.create(rlc=self.rlc, email="test3@law-orga.de")
        RlcUser.objects.create(user=user)
        user = UserProfile.objects.get(email="test3@law-orga.de")
        user.rlc_user.generate_keys()
        assert user.rlc_user.private_key is not None

    def test_accept_works_on_new_user(self):
        user = UserProfile.objects.create(rlc=self.rlc, email="test3@law-orga.de")
        RlcUser.objects.create(user=user)
        user = UserProfile.objects.get(email="test3@law-orga.de")
        user.rlc_user.generate_keys()
        assert user.rlc_user.private_key is not None
        self.rlc.accept_member(self.user, user, self.private_key)

    def test_accept_works(self):
        HasPermission.objects.create(
            permission=Permission.objects.get(name=PERMISSION_ADMIN_MANAGE_USERS),
            user_has_permission=self.user,
        )
        view = RlcUserViewSet.as_view(actions={"post": "accept"})
        rlc_user = self.rlc_user
        self.another_rlc_user.accepted = False
        self.another_rlc_user.save()
        request = self.factory.post("")
        force_authenticate(request, rlc_user.user)
        response = view(request, pk=self.another_rlc_user.pk)
        self.assertEqual(response.status_code, 200)

    def test_unlock_works(self):
        view = RlcUserViewSet.as_view(actions={"post": "unlock"})
        rlc_user = self.rlc_user
        self.another_rlc_user.locked = True
        self.another_rlc_user.save()
        request = self.factory.post("")
        force_authenticate(request, rlc_user.user)
        response = view(request, pk=self.another_rlc_user.pk)
        self.assertEqual(response.status_code, 200)


class UserViewSetErrorTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.rlc = Org.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(
            email="test@test.de", name="Dummy 1", rlc=self.rlc
        )
        self.user.set_password("test")
        self.user.save()
        self.rlc_user = RlcUser.objects.create(
            user=self.user, email_confirmed=True, accepted=True
        )
        self.another_user = UserProfile.objects.create(
            email="test_new@test.de", name="Dummy 2", rlc=self.rlc
        )
        self.another_user.set_password("test")
        self.another_user.save()
        self.another_rlc_user = RlcUser.objects.create(
            user=self.another_user, email_confirmed=True, accepted=True
        )

    def test_create_returns_error_message_on_different_passwords(self):
        view = RlcUserViewSet.as_view(actions={"post": "create"})
        data = {
            "rlc": self.rlc.pk,
            "name": "Test",
            "email": "test2@test.de",
            "password": "test1",
            "password_confirm": "test2",
        }
        request = self.factory.post("/api/users/", data)
        response = view(request)
        self.assertContains(response, "non_field_errors", status_code=400)
        self.assertEqual(response.status_code, 400)

    def test_user_can_not_delete_someone_else(self):
        view = RlcUserViewSet.as_view(actions={"delete": "destroy"})
        url = "/api/users/{}/".format(self.another_rlc_user.pk)
        request = self.factory.delete(url)
        force_authenticate(request, self.rlc_user.user)
        response = view(request, pk=self.another_rlc_user.pk)
        self.assertNotEqual(response.status_code, 204)

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
        self.assertNotEqual(response.status_code, 200)

    def test_login_returns_correct_password_wrong_error(self):
        view = RlcUserViewSet.as_view(actions={"post": "login"})
        data = {
            "email": "test@test.de",
            "password": "falsch",
        }
        request = self.factory.post("/api/users/login/", data)
        response = view(request)
        self.assertContains(response, "non_field_errors", status_code=400)

    def test_login_returns_correct_email_wrong_message(self):
        view = RlcUserViewSet.as_view(actions={"post": "login"})
        data = {
            "email": "falsch",
            "password": "falsch",
        }
        request = self.factory.post("/api/users/login/", data)
        response = view(request)
        self.assertContains(response, "non_field_errors", status_code=400)

    def test_inactive_user_can_not_login(self):
        self.rlc_user.is_active = False
        self.rlc_user.save()
        view = RlcUserViewSet.as_view(actions={"post": "login"})
        data = {
            "email": "test@test.de",
            "password": "test",
        }
        request = self.factory.post("/api/users/login/", data)
        response = view(request)
        self.assertContains(response, "non_field_errors", status_code=400)

    def test_update_denys_without_permission(self):
        view = RlcUserViewSet.as_view(actions={"patch": "partial_update"})
        data = {"phone": "3243214321"}
        request = self.factory.patch("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.another_rlc_user.pk)
        self.assertEqual(response.status_code, 403)


class UserViewSetAccessTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.rlc = Org.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(
            email="test@test.de", name="Dummy 1", rlc=self.rlc
        )
        self.user.set_password("test")
        self.user.save()
        self.rlc_user = RlcUser.objects.create(
            pk=1, user=self.user, email_confirmed=True, accepted=True
        )

    def test_everybody_can_post_to_user_create(self):
        view = RlcUserViewSet.as_view(actions={"post": "create"})
        request = self.factory.post("/api/users/")
        response = view(request)
        self.assertNotEqual(response.status_code, 403)
        self.assertNotEqual(response.status_code, 401)

    def test_not_everytbody_can_hit_retrieve(self):
        view = RlcUserViewSet.as_view(actions={"get": "retrieve"})
        request = self.factory.get("/api/users/1/")
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 401)

    def test_not_everybody_can_hit_update(self):
        view = RlcUserViewSet.as_view(actions={"patch": "update"})
        request = self.factory.patch("/api/users/1/", {})
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 401)

    def test_not_everytbody_can_hit_destroy(self):
        view = RlcUserViewSet.as_view(actions={"delete": "destroy"})
        request = self.factory.delete("/api/users/1/")
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 401)

    def test_not_everytbody_can_hit_list(self):
        view = RlcUserViewSet.as_view(actions={"get": "list"})
        request = self.factory.delete("/api/users/")
        response = view(request)
        self.assertEqual(response.status_code, 401)

    def test_everybody_can_hit_login(self):
        view = RlcUserViewSet.as_view(actions={"post": "login"})
        request = self.factory.post("/api/users/login/")
        response = view(request)
        self.assertNotEqual(response.status_code, 403)
        self.assertNotEqual(response.status_code, 401)

    def test_not_everybody_can_hit_admin(self):
        view = RlcUserViewSet.as_view(actions={"get": "admin"})
        request = self.factory.get("/api/users/admin/")
        response = view(request)
        self.assertEqual(response.status_code, 401)

    def test_everybody_can_hit_statics(self):
        view = RlcUserViewSet.as_view(actions={"get": "statics"})
        request = self.factory.get("/api/users/statics/")
        response = view(request)
        self.assertNotEqual(response.status_code, 401)
        self.assertNotEqual(response.status_code, 403)

    def test_everybody_can_hit_activate(self):
        view = RlcUserViewSet.as_view(actions={"post": "activate"})
        request = self.factory.post("/api/users/1/activate/token-123/")
        response = view(request, pk=1, token="token-123")
        self.assertNotEqual(response.status_code, 403)
        self.assertNotEqual(response.status_code, 401)

    def test_everybody_can_hit_password_reset(self):
        view = RlcUserViewSet.as_view(actions={"post": "password_reset"})
        request = self.factory.post("/api/users/password_reset/")
        response = view(request)
        self.assertNotEqual(response.status_code, 403)
        self.assertNotEqual(response.status_code, 401)

    def test_everybody_can_hit_password_reset_confirm(self):
        view = RlcUserViewSet.as_view(actions={"post": "password_reset_confirm"})
        request = self.factory.post("/api/users/1/password_reset_confirm/")
        response = view(request, pk=1)
        self.assertNotEqual(response.status_code, 403)
        self.assertNotEqual(response.status_code, 401)

    def test_not_everybody_can_hit_unlock(self):
        view = RlcUserViewSet.as_view(actions={"post": "unlock"})
        request = self.factory.post("/api/users/1/unlock/")
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 401)

    def test_not_everybody_can_hit_accept(self):
        view = RlcUserViewSet.as_view(actions={"get": "accept"})
        request = self.factory.post("/api/users/1/accept/")
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 401)
