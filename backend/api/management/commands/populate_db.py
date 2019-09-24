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
from ._factories import UserFactory, ClientFactory, RecordFactory, GroupFactory
from backend.api.models import *
from ._fixtures import Fixtures, AddMethods
from backend.recordmanagement.models import *


class Command(BaseCommand):
    help = 'populates database'

    def add_arguments(self, parser):
        parser.add_argument('--users',
                            default=20,
                            type=int,
                            help='number of fake users to create'
                            )
        parser.add_argument('--clients',
                            default=50,
                            type=int,
                            help='number of fake clients to create'
                            )
        parser.add_argument('--records',
                            default=50,
                            type=int,
                            help='number of fake records to create'
                            )
        parser.add_argument('--groups',
                            default=4,
                            type=int,
                            help='number of fake groups to create'
                            )

    def handle(self, *args, **options):
        Fixtures.create_example_record_tags()
        Fixtures.create_example_permissions()
        Fixtures.create_example_static_users()
        Fixtures.create_example_origin_countries()
        Fixtures.create_rlcs()
        AddMethods.add_to_rlc(2, 1)
        AddMethods.add_to_rlc(1, 2)

        for _ in range(options['users']):
            UserFactory.create(rlcs=(list(Rlc.objects.all())))
        for _ in range(options['clients']):
            ClientFactory.create()
        for _ in range(options['records']):
            RecordFactory.create(tags=(list(RecordTag.objects.all())),
                                 working_on_users=(list(UserProfile.objects.all())))
        for _ in range(options['groups']):
            GroupFactory.create(group_members=(list(UserProfile.objects.all())))
