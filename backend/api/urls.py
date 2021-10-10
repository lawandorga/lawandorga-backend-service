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
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from backend.api import views
from backend.internal.urls import router as internal_router

router = DefaultRouter()
router.registry.extend(internal_router.registry)
router.register("profiles", views.user.UserViewSet, basename='profiles')
router.register("groups", views.GroupViewSet, basename="groups")
router.register("permissions", views.PermissionViewSet, basename="permissions")
router.register("has_permission", views.HasPermissionViewSet, basename="has_permission")
router.register("rlcs", views.RlcViewSet, basename="rlcs")
router.register(
    "user_encryption_keys",
    views.UserEncryptionKeysViewSet,
    basename="user_encryption_keys",
)
router.register("users_rlc_keys", views.UsersRlcKeysViewSet, basename="users_rlc_keys")
router.register("notifications", views.NotificationViewSet)
router.register("notification_groups", views.NotificationGroupViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("permissions_for_group/<int:pk>/", views.PermissionsForGroupViewSet.as_view()),
    path("has_permission_statics/", views.HasPermissionStaticsViewSet.as_view()),
    path("user_has_permissions/", views.UserHasPermissionsViewSet.as_view()),
]
