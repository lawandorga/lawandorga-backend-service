from typing import Union

from django.urls import URLPattern, URLResolver, include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()

router.register("statistic_users", views.StatisticsUserViewSet)

urlpatterns: list[Union[URLPattern, URLResolver]] = [
    path("api/", include(router.urls)),
    path("api/logout/", api.command__logout),
    path("api/rlc_users/", include(api.rlc_user_router.urls)),
    path("api/users/", include(api.users_router.urls)),
    path("api/statistics_users/", include(api.statistics_user_router.urls)),
    path("api/matrix_users/", include(api.matrix_user_router.urls)),
    path("api/keys/", include(api.keys_router.urls)),
    path("api/auth/query/", include(api.query_router.urls)),
    path(
        "auth/password_reset/",
        views.CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "auth/password_reset_done/",
        views.CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "auth/password_reset_confirm/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "auth/password_reset_complete/",
        views.CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
