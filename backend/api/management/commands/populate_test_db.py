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
from ._fixtures import Fixtures
from backend.api.models import UserProfile, Rlc


class Command(BaseCommand):
    help = 'populates database for test environment'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        Fixtures.create_handmade_examples()
        Fixtures.create_real_permissions()
        # Command.add_admin_account()
        Command.add_standard_account()

    @staticmethod
    def add_admin_account():
        user = UserProfile(name="Bruce Wayne", email="jehob@web.de", is_superuser=True)
        user.set_password("qwe123")
        user.save()

    @staticmethod
    def add_standard_account():
        rlc = Rlc.objects.first()
        user = UserProfile(name="Bruce Wayne", email="abc@web.de", rlc_id=rlc.id)
        user.set_password("qwe123")
        user.save()
