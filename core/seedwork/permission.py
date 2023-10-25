from typing import Dict, Optional


class CheckPermissionWall:
    permission_wall: Optional[Dict[str, str]] = None

    def check_permissions(self, request):
        check = super().check_permissions(request)

        if self.permission_wall is None:
            raise ValueError("You need to implement the permission_wall.")

        if self.action in self.permission_wall:
            permission = self.permission_wall[self.action]
            if not request.user.has_permission(permission):
                message = "You need the permission '{}' to do this.".format(permission)
                self.permission_denied(request, message, 403)

        return check
