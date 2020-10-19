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

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View
import logging


# TODO: what to do with this?? custom permissions?
class UpdateOwnProfile(permissions.BasePermission):
    """allow users to edit their own profile"""

    def has_object_permission(self, request, view, obj):
        """check user is trying to edit their own profile"""

        if request.method in permissions.SAFE_METHODS or request.user.is_superuser:
            return True

        return obj.id == request.user.id or request.user.is_staff


class EditRecord(permissions.BasePermission):
    def has_permission(self, request, view):
        return True


class OnlySuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class EditPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        return request.user.is_superuser


class OriginCountry(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == "GET":
            return True
        else:
            return False


class GetOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser or request.method == "GET":
            return True
        return False


class IsAuthenticatedLogging(permissions.BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        if bool(request.user and request.user.is_authenticated):
            logger = logging.getLogger(__name__)
            logger.info(
                "general_activity user:"
                + str(request.user.id)
                + "; rlc:"
                + str(request.user.rlc.id)
            )
            print(
                "general_activity user:"
                + str(request.user.id)
                + "; rlc:"
                + str(request.user.rlc.id)
            )
            return True
        return False


class OnlyGet(permissions.BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        return request.method == "GET"
