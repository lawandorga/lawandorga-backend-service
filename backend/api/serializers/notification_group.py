#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
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
from backend.api.models.notification_group import NotificationGroup
from backend.api.serializers import NotificationSerializer
from rest_framework import serializers


class NotificationGroupOrderedSerializer(serializers.ModelSerializer):
    notifications = serializers.SerializerMethodField()

    class Meta:
        model = NotificationGroup
        fields = "__all__"

    def get_notifications(self, obj: NotificationGroup):
        return NotificationSerializer(
            obj.notifications.all().order_by("-created"), many=True, read_only=True
        ).data
