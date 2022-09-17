from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()

router.register("statistics/general", views.StatisticsViewSet, basename="statistic")
router.register("statistics/rlc", views.RlcStatisticsViewSet, basename="rlc_statistic")


urlpatterns = [
    path("", include(router.urls)),
    path("statistics/error/", include(api.error_statistics_router.urls)),
]
