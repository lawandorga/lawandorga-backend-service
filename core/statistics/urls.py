from django.urls import include, path

from . import api

urlpatterns = [
    path("statistics/individual/", include(api.individual_statistics_router.urls)),
    path("statistics/general/", include(api.general_statistics_router.urls)),
    path("statistics/error/", include(api.error_statistics_router.urls)),
    path("statistics/record/", include(api.record_statistics_router.urls)),
    path("statistics/org/", include(api.rlc_statistics_router.urls)),
]
