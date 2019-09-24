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

from django.core.management.base import BaseCommand

from backend.api.models import *
from backend.recordmanagement.models import *
from backend.static.permissions import PERMISSION_MANAGE_PERMISSIONS_RLC, PERMISSION_VIEW_PERMISSIONS_RLC


class Command(BaseCommand):
    help = 'creates new rlc'

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')
        parser.add_argument('--admin_email', type=str)
        parser.add_argument('--admin_name', type=str)
        parser.add_argument('--admin_password', type=str)
        parser.add_argument('--rlc_name', type=str)

    def handle(self, *args, **options):
        # self.stdout.write("test", ending='')
        # self.stdout.write(options['admin_password'], ending='')
        # self.stdout.write(options['rlc_name'], ending='')

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

        rlc_object = Rlc(name=options['rlc_name'])
        rlc_object.save()
        admin_user = UserProfile(email=options['admin_email'], rlc=rlc_object, name=options['admin_name'])
        admin_user.set_password(options['admin_password'])
        admin_user.save()

        manage_permissions_has_permission = HasPermission(
            permission=Permission.objects.filter(name=PERMISSION_MANAGE_PERMISSIONS_RLC).first(),
            user_has_permission=admin_user, permission_for_rlc=rlc_object)
        manage_permissions_has_permission.save()

        view_permission_has_permission = HasPermission(
            permission=Permission.objects.filter(name=PERMISSION_VIEW_PERMISSIONS_RLC).first(),
            user_has_permission=admin_user, permission_for_rlc=rlc_object)
        view_permission_has_permission.save()


