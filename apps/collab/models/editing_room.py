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
from apps.collab.models.text_document import TextDocument
from apps.static.encryption import AESEncryption
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.db import models


def generate_room_id():
    length = 32
    prefix = "law-orga-"
    pot_room_id = prefix + get_random_string(length)
    while True:
        try:
            EditingRoom.objects.get(room_id=pot_room_id)
            pot_room_id = prefix + get_random_string(length)
        except:
            return pot_room_id


class EditingRoom(models.Model):
    created = models.DateTimeField(default=timezone.now)
    document = models.OneToOneField(TextDocument, on_delete=models.CASCADE)

    room_id = models.CharField(
        max_length=255, default=generate_room_id, auto_created=True, unique=True
    )
    password = models.CharField(
        max_length=255,
        default=AESEncryption.generate_secure_key,
        auto_created=True,
        unique=True,
    )

    # TODO: number of connected users
