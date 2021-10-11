from rest_framework import permissions


class OnlySuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser
