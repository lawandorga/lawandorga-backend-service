from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("statistics", views.StatisticsViewSet, basename="statistic")
router.register("rlc_statistics", views.RlcStatisticsViewSet, basename="rlc_statistic")
