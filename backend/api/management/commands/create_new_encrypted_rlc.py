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

from django.core.management.base import BaseCommand

from backend.api.models import Group, HasPermission, Permission, Rlc, UserProfile, RlcEncryptionKeys, UserEncryptionKeys, UsersRlcKeys
from backend.static.encryption import RSAEncryption, AESEncryption
from backend.static.permissions import PERMISSION_MANAGE_GROUPS_RLC, PERMISSION_MANAGE_PERMISSIONS_RLC, \
    PERMISSION_VIEW_PERMISSIONS_RLC


class Command(BaseCommand):
    help = 'creates new rlc'

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')
        parser.add_argument('--admin_email', type=str)
        parser.add_argument('--admin_name', type=str)
        parser.add_argument('--admin_password', type=str)
        parser.add_argument('--rlc_name', type=str)

    def handle(self, *args, **options):
        if 'rlc_name' not in options or options['rlc_name'] is None:
            self.stdout.write("rlc_name missing\r\n", ending='')
            return
        if 'admin_email' not in options or options['admin_email'] is None:
            self.stdout.write("admin_email missing\r\n", ending='')
            return
        if 'admin_name' not in options or options['admin_name'] is None:
            self.stdout.write("admin_name missing\r\n", ending='')
            return
        if 'admin_password' not in options or options['admin_password'] is None:
            self.stdout.write("admin_password missing\r\n", ending='')
            return

        rlc = Rlc(name=options['rlc_name'])
        rlc.save()
        admin_user = UserProfile(email=options['admin_email'], rlc=rlc, name=options['admin_name'])
        admin_user.set_password(options['admin_password'])
        admin_user.save()

        admin_private, admin_public = RSAEncryption.generate_keys()
        admin_keys = UserEncryptionKeys(user=admin_user, private_key=admin_private, public_key=admin_public)
        admin_keys.save()

        rlc_aes = AESEncryption.generate_secure_key()
        rlc_private, rlc_public = RSAEncryption.generate_keys()
        encrypted_private = AESEncryption.encrypt(rlc_private, rlc_aes)
        rlc_keys = RlcEncryptionKeys(rlc=rlc, encrypted_private_key=encrypted_private, public_key=rlc_public)
        rlc_keys.save()
        for_user_encrypted_rlc_key = RSAEncryption.encrypt(rlc_aes, admin_public)
        admin_rlc_keys = UsersRlcKeys(user=admin_user, rlc=rlc, encrypted_key=for_user_encrypted_rlc_key)
        admin_rlc_keys.save()

        admin_group = Group(name='Administrator*innen', visible=False, from_rlc=rlc)
        admin_group.save()
        admin_group.group_members.add(admin_user)
        admin_group.save()

        manage_permissions_has_permission = HasPermission(
            permission=Permission.objects.filter(name=PERMISSION_MANAGE_PERMISSIONS_RLC).first(),
            group_has_permission=admin_group, permission_for_rlc=rlc)
        manage_permissions_has_permission.save()

        view_permission_has_permission = HasPermission(
            permission=Permission.objects.filter(name=PERMISSION_VIEW_PERMISSIONS_RLC).first(),
            group_has_permission=admin_group, permission_for_rlc=rlc)
        view_permission_has_permission.save()

        manage_groups = HasPermission(
            permission=Permission.objects.filter(name=PERMISSION_MANAGE_GROUPS_RLC).first(),
            group_has_permission=admin_group, permission_for_rlc=rlc
        )
        manage_groups.save()
