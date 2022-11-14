from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from core.models import RlcUser, StatisticUser, UserProfile
from core.rlc.models import Org
from core.views import StatisticsUserViewSet


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

    def test_statics(self):
        view = StatisticsUserViewSet.as_view(actions={"get": "statics"})
        request = self.factory.get("")
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, "user", status_code=200)

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
        self.user.check_password("pass1234!")

    def test_change_password_blocked_with_rlc_user_existing(self):
        rlc = Org.objects.create(name="Test")
        RlcUser.objects.create(
            org=rlc,
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
