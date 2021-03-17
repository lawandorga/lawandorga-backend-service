#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
from backend.recordmanagement import urls as record_urls
from rest_framework.routers import DefaultRouter
from backend.files import urls as file_urls
from django.urls import path, include
from backend.api import views

router = DefaultRouter()
router.register("profiles", views.user.UserProfileViewSet)
router.register("login", views.LoginViewSet, basename="login")
router.register(
    "create_profile", views.UserProfileCreatorViewSet, basename="create_profile"
)
router.register("groups", views.GroupViewSet, basename="groups")
router.register("permissions", views.PermissionViewSet, basename="permissions")
router.register("has_permission", views.HasPermissionViewSet, basename="has_permission")
router.register("rlcs", views.RlcViewSet, basename="rlcs")
router.register(
    "forgot_password_links",
    views.ForgotPasswordViewSet,
    basename="forgot_password_links",
)
router.register(
    "new_user_request", views.NewUserRequestViewSet, basename="new_user_request"
)
router.register(
    "user_activation_links",
    views.UserActivationBackendViewSet,
    basename="user_activation_links",
)
router.register(
    "user_encryption_keys",
    views.UserEncryptionKeysViewSet,
    basename="user_encryption_keys",
)
router.register("users_rlc_keys", views.UsersRlcKeysViewSet, basename="users_rlc_keys")
router.register("notifications", views.NotificationViewSet, basename="notifications")
router.register(
    "notification_groups", views.NotificationGroupViewSet, basename="notifications"
)

urlpatterns = [
    path("", include(router.urls)),
    path("records/", include(record_urls)),
    path("files/", include(file_urls)),
    path("get_rlcs/", views.GetRlcsViewSet.as_view()),
    path("forgot_password/", views.ForgotPasswordUnauthenticatedViewSet.as_view()),
    path("reset_password/<int:id>/", views.ResetPasswordViewSet.as_view()),
    path("group_members/", views.GroupMembersViewSet.as_view()),
    path("permissions_for_group/<int:pk>/", views.PermissionsForGroupViewSet.as_view()),
    path("has_permission_statics/", views.HasPermissionStaticsViewSet.as_view()),
    path(
        "check_user_activation_link/<int:id>/",
        views.CheckUserActivationLinkViewSet.as_view(),
    ),
    path(
        "activate_user_activation_link/<int:id>/",
        views.UserActivationLinkViewSet.as_view(),
    ),
    path("new_user_request_admit/", views.NewUserRequestAdmitViewSet.as_view()),
    path("logout/", views.LogoutViewSet.as_view()),
    path("inactive_users/", views.InactiveUsersViewSet.as_view()),
    path("user_has_permissions/", views.UserHasPermissionsViewSet.as_view()),
    path("my_rlc_settings/", views.RlcSettingsMineViewSet.as_view()),
    path("unread_notifications/", views.UnreadNotificationsViewSet.as_view()),
]
