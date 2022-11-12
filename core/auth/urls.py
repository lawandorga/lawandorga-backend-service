from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()

router.register("profiles", views.RlcUserViewSet, basename="profiles")
router.register("statistic_users", views.StatisticsUserViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("session_login/", api.command__login),
    path("rlc_users/", include(api.rlc_user_router.urls)),
    path("keys/", include(api.keys_router.urls)),
]
