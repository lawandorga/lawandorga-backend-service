from typing import Union

from django.urls import URLPattern, URLResolver, include, path

from . import api, views

api_urlpatterns: list[Union[URLPattern, URLResolver]] = [
    path("org_users/", include(api.org_user_router.urls)),
    path("statistics_users/", include(api.statistics_user_router.urls)),
    path("keys/", include(api.keys_router.urls)),
    path("query/", include(api.query_router.urls)),
]

view_urlpatterns: list[Union[URLPattern, URLResolver]] = [
    path("user/register/", views.CustomRegisterView.as_view(), name="register"),
    path(
        "user/register/successful/",
        views.CustomRegisterDoneView.as_view(),
        name="register_done",
    ),
    path("user/logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("user/login/", views.CustomLoginView.as_view(), name="login"),
    path(
        "user/password_reset/",
        views.CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "user/password_reset_done/",
        views.CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "user/password_reset_confirm/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "user/password_reset_complete/",
        views.CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("mfa/status/", views.MfaStatusView.as_view(), name="mfa_status"),
    path("mfa/setup/", views.MfaSetupView.as_view(), name="mfa_setup"),
    path(
        "mfa/enable/",
        views.MfaEnableView.as_view(),
        name="mfa_enable",
    ),
    path(
        "mfa/disable/",
        views.MfaDisableView.as_view(),
        name="mfa_disable",
    ),
    path("mfa/login/", views.MfaLoginView.as_view(), name="mfa_login"),
]
