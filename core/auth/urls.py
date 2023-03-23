from typing import Union

from django.urls import URLPattern, URLResolver, include, path

from . import api, views

urlpatterns: list[Union[URLPattern, URLResolver]] = [
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
    path("auth/mfa/status/", views.MfaStatusView.as_view(), name="mfa_status"),
    path("auth/mfa/setup/", views.MfaSetupView.as_view(), name="mfa_setup"),
    path("auth/mfa/enable/<int:pk>/", views.MfaEnableView.as_view(), name="mfa_enable"),
    path("auth/mfa/login/", views.MfaLoginView.as_view(), name="mfa_login"),
    # path('auth/mfa/remove/', views.MfaRemoveView.as_view(),
    # name="mfa_remove"),
]
