from typing import Union

from django.urls import URLPattern, URLResolver, include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()

router.register("profiles", views.RlcUserViewSet, basename="profiles")
router.register("statistic_users", views.StatisticsUserViewSet)


urlpatterns: list[Union[URLPattern, URLResolver]] = [
    path("", include(router.urls)),
    path("logout/", api.command__logout),
    path("rlc_users/", include(api.rlc_user_router.urls)),
    path("statistics_users/", include(api.statistics_user_router.urls)),
    path("keys/", include(api.keys_router.urls)),
]
