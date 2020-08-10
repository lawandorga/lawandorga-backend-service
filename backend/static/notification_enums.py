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
from enum import Enum


class NotificationGroupType(Enum):
    """
    Enum for notification event object
    these regard the models which the notification is about
    """
    RECORD = "RECORD"
    RECORD_PERMISSION_REQUEST = "RECORD_PERMISSION_REQUEST"
    RECORD_DELETION_REQUEST = "RECORD_DELETION_REQUEST"
    USER_REQUEST = "USER_REQUEST"
    GROUP = "GROUP"
    FILE = "FILE"   # ?

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class NotificationEvent(Enum):
    """
    enum for notification events types
    contains the action which was performed
    """
    CREATED = "CREATED"
    DELETED = "DELETED"
    MOVED = "MOVED"
    UPDATED = "UPDATED"
    ADDED = "ADDED"
    REMOVED = "REMOVED"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class NotificationType(Enum):
    RECORD_MESSAGE = "RECORD_MESSAGE"
    RECORD_UPDATE = "RECORD_UPDATE"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
