from typing import Union

from django.urls import URLPattern, URLResolver, include, path

from . import api, views

urlpatterns: list[Union[URLPattern, URLResolver]] = [
    path("api/rlc_users/", include(api.rlc_user_router.urls)),
    path("api/statistics_users/", include(api.statistics_user_router.urls)),
    path("api/matrix_users/", include(api.matrix_user_router.urls)),
    path("api/keys/", include(api.keys_router.urls)),
    path("api/auth/query/", include(api.query_router.urls)),
    path("auth/user/register/", views.CustomRegisterView.as_view(), name="register"),
    path(
        "auth/user/register/successful/",
        views.CustomRegisterDoneView.as_view(),
        name="register_done",
    ),
    path("auth/user/logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("auth/user/login/", views.CustomLoginView.as_view(), name="login"),
    path(
        "auth/user/password_reset/",
        views.CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "auth/user/password_reset_done/",
        views.CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "auth/user/password_reset_confirm/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "auth/user/password_reset_complete/",
        views.CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("auth/mfa/status/", views.MfaStatusView.as_view(), name="mfa_status"),
    path("auth/mfa/setup/", views.MfaSetupView.as_view(), name="mfa_setup"),
    path(
        "auth/mfa/enable/",
        views.MfaEnableView.as_view(),
        name="mfa_enable",
    ),
    path(
        "auth/mfa/disable/",
        views.MfaDisableView.as_view(),
        name="mfa_disable",
    ),
    path("auth/mfa/login/", views.MfaLoginView.as_view(), name="mfa_login"),
]
