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

import factory.django
from random import randint
from backend.api.models import UserProfile, Rlc, Group
from backend.recordmanagement.models import Client, OriginCountry, Record


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    email = factory.Faker('email')
    name = factory.Faker('name')
    phone_number = factory.Faker('phone_number')
    is_active = True
    is_staff = False

    @factory.post_generation
    def rlcs(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.rlc_members.add(extracted[randint(0, extracted.__len__() - 1)])


class ClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Client

    name = factory.Faker('name')
    note = factory.Faker('text')
    phone_number = factory.Faker('phone_number')
    birthday = factory.Faker('date_this_decade')
    origin_country = factory.Iterator(OriginCountry.objects.all())
    created_on = factory.Faker('date_this_year')
    last_edited = factory.Faker('date_time_this_month')


class RecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Record

    creator = factory.Iterator(UserProfile.objects.all())
    from_rlc = factory.Iterator(Rlc.objects.all())
    created_on = factory.Faker('date_this_year')
    last_edited = factory.Faker('date_time_this_month')
    client = factory.Iterator(Client.objects.all())
    first_contact_date = factory.Faker('date_this_year')
    last_contact_date = factory.Faker('date_time_this_month')
    record_token = factory.Faker('isbn13')
    note = factory.Faker('text')
    state = factory.Faker('random_element', elements=[e[0] for e in Record.record_states_possible])

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.tagged.add(extracted[randint(0, extracted.__len__() - 1)])

    @factory.post_generation
    def working_on_users(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.working_on_record.add(extracted[randint(0, extracted.__len__() - 1)])
            self.working_on_record.add(extracted[randint(0, extracted.__len__() - 1)])


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
    
    creator = factory.Iterator(UserProfile.objects.all())
    from_rlc = factory.Iterator(Rlc.objects.all())
    name = factory.Faker('word', ext_word_list=[
        'Network ressort', 'Translation ressort', 'It ressort', 'Board', 
    ])
    visible = True

    @factory.post_generation
    def group_members(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for _ in range(10, 20):
                self.group_members.add(
                    extracted[randint(0, extracted.__len__() - 1)])
