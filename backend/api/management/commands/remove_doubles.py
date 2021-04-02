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

from django.core.management.base import BaseCommand

from backend.api.models import UserProfile, UsersRlcKeys, Rlc
from backend.recordmanagement.models import EncryptedRecord, RecordEncryption


class Command(BaseCommand):
    help = "removes doubles"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        UserProfile.objects.filter(rlc=None).delete()

        for rlc in Rlc.objects.all():
            records = EncryptedRecord.objects.filter(from_rlc=rlc)
            users = UserProfile.objects.filter(rlc=rlc)
            for user in users:
                for record in records:
                    keys = RecordEncryption.objects.filter(user=user, record=record)
                    if keys.count() > 1:
                        keys.exclude(id=keys.first().id).delete()

                enc_keys = UsersRlcKeys.objects.filter(user=user)
                if enc_keys.count() > 1:
                    enc_keys.exclude(id=enc_keys.first().id).delete()

        # for  user in UserProfile.objects.all():
        #     for record in EncryptedRecord.objects.filter(from_rlc=user.rlc).all():
        #         keys = RecordEncryption.objects.filter(user=user, record=record)
        #         if keys.count() > 1:
        #             keys.exclude(id=keys.first().id).delete()
        #
        #     enc_keys = UsersRlcKeys.objects.filter(user=user)
        #     if enc_keys.count() > 1:
        #         enc_keys.exclude(id=enc_keys.first().id).delete()
