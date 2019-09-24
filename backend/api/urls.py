#  rlcapp - record and organization management software for refugee law clinics
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


from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from . import views
from ..recordmanagement import urls

router = DefaultRouter()
router.register('profiles', views.user.UserProfileViewSet)
router.register('login', views.LoginViewSet, base_name='login')
router.register('create_profile', views.UserProfileCreatorViewSet,
                base_name='create_profile')
router.register('groups', views.GroupViewSet, base_name='groups')
router.register('permissions', views.PermissionViewSet, base_name='permissions')
router.register('has_permission', views.HasPermissionViewSet, base_name="has_permission")
router.register('rlcs', views.RlcViewSet, base_name='rlcs')
router.register('forgot_password_links', views.ForgotPasswordViewSet, base_name="forgot_password_links")
router.register('new_user_request', views.NewUserRequestViewSet, base_name="new_user_request")
router.register('user_activation_links', views.UserActivationBackendViewSet, base_name="user_activation_links")

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'^records/', include(urls)),
    url(r'send_email/', views.SendEmailViewSet.as_view()),
    url(r'get_rlcs/', views.GetRlcsViewSet.as_view()),
    url(r'storage_up/', views.StorageUploadViewSet.as_view()),
    url(r'storage_down/', views.StorageDownloadViewSet.as_view()),
    url(r'forgot_password/', views.ForgotPasswordUnauthenticatedViewSet.as_view()),
    url(r'reset_password/(?P<id>.+)/$', views.ResetPasswordViewSet.as_view()),
    url(r'group_member/', views.GroupMemberViewSet.as_view()),
    url(r'permissions_for_group/(?P<pk>.+)/$', views.PermissionsForGroupViewSet.as_view()),
    url(r'has_permission_statics/', views.HasPermissionStaticsViewSet.as_view()),
    url(r'check_user_activation_link/(?P<id>.+)/$', views.CheckUserActivationLinkViewSet.as_view()),
    url(r'activate_user_activation_link/(?P<id>.+)/$', views.UserActivationLinkViewSet.as_view()),
    url(r'new_user_request_admit/', views.NewUserRequestAdmitViewSet.as_view()),
    url(r'logout/', views.LogoutViewSet.as_view()),
    url(r'inactive_users/', views.InactiveUsersViewSet.as_view()),
    url(r'user_has_permissions/', views.UserHasPermissionsViewSet.as_view()),
]
