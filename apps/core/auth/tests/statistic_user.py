from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.core.models import RlcUser, StatisticUser, UserProfile
from apps.core.views import StatisticsUserViewSet


class StatisticUserUserBase:
    def setUp(self):
        self.user = UserProfile.objects.create(
            email="dummy@law-orga.de", name="Dummy 1"
        )
        self.user.set_password(settings.DUMMY_USER_PASSWORD)
        self.user.save()
        self.statistic_user = StatisticUser.objects.create(user=self.user)
        self.factory = APIRequestFactory()


class StatisticsUserViewSetTests(StatisticUserUserBase, TestCase):
    def login(self, email="dummy@law-orga.de", password=settings.DUMMY_USER_PASSWORD):
        view = StatisticsUserViewSet.as_view(actions={"post": "login"})
        data = {
            "email": email,
            "password": password,
        }
        request = self.factory.post("", data)
        response = view(request)
        return response

    def test_login(self):
        response = self.login()
        self.assertContains(response, "user", status_code=200)
        self.assertContains(response, "access", status_code=200)
        self.assertContains(response, "refresh", status_code=200)

    def test_statics(self):
        view = StatisticsUserViewSet.as_view(actions={"get": "statics"})
        request = self.factory.get("")
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, "user", status_code=200)

    def test_refresh(self):
        # get a token
        view = StatisticsUserViewSet.as_view(actions={"post": "login"})
        data = {
            "email": "dummy@law-orga.de",
            "password": settings.DUMMY_USER_PASSWORD,
        }
        request = self.factory.post("", data)
        response = view(request)
        refresh = response.data["refresh"]
        # check refresh
        view = StatisticsUserViewSet.as_view(actions={"post": "refresh"})
        data = {"refresh": refresh}
        request = self.factory.post("", data)
        response = view(request)
        self.assertContains(response, "access", status_code=200)
        self.assertContains(response, "refresh", status_code=200)

    def test_change_password(self):
        view = StatisticsUserViewSet.as_view(actions={"post": "change_password"})
        data = {
            "current_password": settings.DUMMY_USER_PASSWORD,
            "new_password": "pass1234!",
            "new_password_confirm": "pass1234!",
        }
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        response = self.login(password="pass1234!")
        self.assertEqual(response.status_code, 200)

    def test_login_blocked_without_statistic_user(self):
        user = UserProfile.objects.create(email="tester@law-orga.de", name="Tester")
        user.set_password(settings.DUMMY_USER_PASSWORD)
        user.save()
        response = self.login(email=user.email)
        self.assertContains(response, "non_field_errors", status_code=400)

    def test_change_password_blocked_with_rlc_user_existing(self):
        RlcUser.objects.create(
            user=self.user,
            accepted=True,
            email_confirmed=True,
            locked=False,
            is_active=True,
        )
        view = StatisticsUserViewSet.as_view(actions={"post": "change_password"})
        data = {
            "current_password": settings.DUMMY_USER_PASSWORD,
            "new_password": "pass1234!",
            "new_password_confirm": "pass1234!",
        }
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, "detail", status_code=400)
