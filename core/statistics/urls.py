from django.urls import include, path

from . import api

urlpatterns = [
    path("individual/", include(api.individual_statistics_router.urls)),
    path("general/", include(api.general_statistics_router.urls)),
    path("error/", include(api.error_statistics_router.urls)),
    path("record/", include(api.record_statistics_router.urls)),
    path("org/", include(api.rlc_statistics_router.urls)),
]
