#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2021  Dominik Walser
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

from django.db import models

from backend.api.models import Group
from backend.collab.models import CollabPermission, CollabDocument


class PermissionForCollabDocument(models.Model):
    permission = models.ForeignKey(
        CollabPermission,
        related_name="in_permission_for_document",
        null=False,
        on_delete=models.CASCADE,
    )
    group_has_permission = models.ForeignKey(
        Group,
        related_name="group_has_collab_permission",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    document = models.ForeignKey(
        CollabDocument,
        related_name="collab_permissions",
        on_delete=models.CASCADE,
        null=False,
    )

    class Meta:
        unique_together = ["permission", "group_has_permission", "document"]
