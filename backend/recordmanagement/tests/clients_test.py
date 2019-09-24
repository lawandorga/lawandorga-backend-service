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


from rest_framework.test import APIClient
from django.test import TransactionTestCase
from backend.recordmanagement.models import Client, OriginCountry
from backend.api.tests.fixtures import CreateFixtures
from backend.api.tests.statics import StaticTestMethods
# TODO: test destroy, patch, put


class ClientsTests(TransactionTestCase):
    def setUp(self):
        self.client = StaticTestMethods.force_authentication()
        self.base_url = '/api/records/clients/'
        CreateFixtures.create_sample_countries()

    def test_create_client_success(self):
        clients_before = Client.objects.count()
        origin_country = list(OriginCountry.objects.all())[0]
        clients_in_country_before = origin_country.clients.count()
        to_post = {
            'name': 'First Client',
            'note': 'the important note',
            'phone_number': 1991923019,
            'birthday': '1990-12-24',
            'origin_country': origin_country.id
        }
        response = self.client.post(self.base_url, to_post)
        clients_after = Client.objects.count()

        self.assertTrue(response.status_code == 201)
        self.assertTrue(clients_after == clients_before + 1)
        self.assertTrue(list(OriginCountry.objects.all())[0].clients.count() == clients_in_country_before + 1)

    # TODO: test success for: (and empty) no note, no phone, no birthday, no origincountry (?)

    def test_create_client_error_unauthenticated(self):
        client = APIClient()
        clients_before = Client.objects.count()
        origin_country = list(OriginCountry.objects.all())[0]
        clients_in_country_before = origin_country.clients.count()
        to_post = {
            'name': 'First Client',
            'note': 'the important note',
            'phone_number': 1991923019,
            'birthday': '1990-12-24',
            'origin_country': origin_country.id
        }
        response = client.post(self.base_url, to_post)
        clients_after = Client.objects.count()

        self.assertTrue(response.status_code == 401)
        self.assertTrue(clients_after == clients_before)
        self.assertTrue(list(OriginCountry.objects.all())[0].clients.count() == clients_in_country_before)

    def test_create_client_error_double_name(self):
        clients_before = Client.objects.count()
        origin_country = list(OriginCountry.objects.all())[0]
        clients_in_country_before = origin_country.clients.count()
        to_post = {
            'name': 'First Client',
            'note': 'the important note',
            'phone_number': 1991923019,
            'birthday': '1990-12-24',
            'origin_country': origin_country.id
        }
        self.client.post(self.base_url, to_post)
        to_post = {
            'name': 'First Client',
            'note': 'other important note',
            'phone_number': 12478349,
            'birthday': '1995-10-14',
            'origin_country': origin_country.id
        }
        response = self.client.post(self.base_url, to_post)
        clients_after = Client.objects.count()

        self.assertTrue(response.status_code == 400)
        self.assertTrue(clients_after == clients_before + 1)
        self.assertTrue(list(OriginCountry.objects.all())[0].clients.count() == clients_in_country_before + 1)

    def test_create_client_error_no_name(self):
        clients_before = Client.objects.count()
        origin_country = list(OriginCountry.objects.all())[0]
        clients_in_country_before = origin_country.clients.count()
        to_post = {
            'note': 'the important note',
            'phone_number': 1991923019,
            'birthday': '1990-12-24',
            'origin_country': origin_country.id
        }
        response = self.client.post(self.base_url, to_post)
        clients_after = Client.objects.count()

        self.assertTrue(response.status_code == 400)
        self.assertTrue(clients_after == clients_before)
        self.assertTrue(list(OriginCountry.objects.all())[0].clients.count() == clients_in_country_before)

    def test_create_client_error_empty_name(self):
        clients_before = Client.objects.count()
        origin_country = list(OriginCountry.objects.all())[0]
        clients_in_country_before = origin_country.clients.count()
        to_post = {
            'name': '',
            'note': 'the important note',
            'phone_number': 1991923019,
            'birthday': '1990-12-24',
            'origin_country': origin_country.id
        }
        response = self.client.post(self.base_url, to_post)
        clients_after = Client.objects.count()

        self.assertTrue(response.status_code == 400)
        self.assertTrue(clients_after == clients_before)
        self.assertTrue(list(OriginCountry.objects.all())[0].clients.count() == clients_in_country_before)

    def test_create_client_error_wrong_phone_number_too_short(self):
        clients_before = Client.objects.count()
        origin_country = list(OriginCountry.objects.all())[0]
        clients_in_country_before = origin_country.clients.count()
        to_post = {
            'name': 'First Client',
            'note': 'the important note',
            'phone_number': 22,
            'birthday': '1990-12-24',
            'origin_country': origin_country.id
        }
        response = self.client.post(self.base_url, to_post)
        clients_after = Client.objects.count()

        self.assertTrue(response.status_code == 400)
        self.assertTrue(clients_after == clients_before)
        self.assertTrue(list(OriginCountry.objects.all())[0].clients.count() == clients_in_country_before)

    def test_create_client_error_wrong_phone_number_too_long(self):
        clients_before = Client.objects.count()
        origin_country = list(OriginCountry.objects.all())[0]
        clients_in_country_before = origin_country.clients.count()
        to_post = {
            'name': 'First Client',
            'note': 'the important note',
            'phone_number': 222222222222222222,
            'birthday': '1990-12-24',
            'origin_country': origin_country.id
        }
        response = self.client.post(self.base_url, to_post)
        clients_after = Client.objects.count()

        self.assertTrue(response.status_code == 400)
        self.assertTrue(clients_after == clients_before)
        self.assertTrue(list(OriginCountry.objects.all())[0].clients.count() == clients_in_country_before)

    def test_create_client_error_wrong_birthday_format(self):
        clients_before = Client.objects.count()
        origin_country = list(OriginCountry.objects.all())[0]
        clients_in_country_before = origin_country.clients.count()
        to_post = {
            'name': 'First Client',
            'note': 'the important note',
            'phone_number': 1235364522,
            'birthday': '1990/12/4',
            'origin_country': origin_country.id
        }
        response = self.client.post(self.base_url, to_post)
        clients_after = Client.objects.count()

        self.assertTrue(response.status_code == 400)
        self.assertTrue(clients_after == clients_before)
        self.assertTrue(list(OriginCountry.objects.all())[0].clients.count() == clients_in_country_before)

    def test_create_client_error_wrong_birthday_date(self):
        clients_before = Client.objects.count()
        origin_country = list(OriginCountry.objects.all())[0]
        clients_in_country_before = origin_country.clients.count()
        to_post = {
            'name': 'First Client',
            'note': 'the important note',
            'phone_number': 1235364522,
            'birthday': '1990-13-4',
            'origin_country': origin_country.id
        }
        response = self.client.post(self.base_url, to_post)
        clients_after = Client.objects.count()

        self.assertTrue(response.status_code == 400)
        self.assertTrue(clients_after == clients_before)
        self.assertTrue(list(OriginCountry.objects.all())[0].clients.count() == clients_in_country_before)

    def test_create_client_error_wrong_country(self):
        clients_before = Client.objects.count()
        to_post = {
            'name': 'First Client',
            'note': 'the important note',
            'phone_number': 1235364522,
            'birthday': '1990-13-4',
            'origin_country': -1
        }
        response = self.client.post(self.base_url, to_post)
        clients_after = Client.objects.count()

        self.assertTrue(response.status_code == 400)
        self.assertTrue(clients_after == clients_before)

    def test_show_all_clients_unauthenticated(self):
        client = APIClient()
        response = client.get(self.base_url)
        self.assertTrue(response.status_code == 401)

    def test_create_multiple_clients_success(self):
        before = Client.objects.count()
        created = CreateFixtures.create_sample_clients()
        after = Client.objects.count()
        self.assertTrue(after == created.__len__() + before)

    def test_edit_put_succcess(self):
        origin_country = list(OriginCountry.objects.all())[0]
        to_post = {
            'name': 'First Client',
            'note': 'the important note',
            'phone_number': 1991923019,
            'birthday': '1990-12-24',
            'origin_country': origin_country.id
        }
        response = self.client.post(self.base_url, to_post)
        clients = Client.objects.count()
        to_post['name'] = 'Still First Client'
        response = self.client.put(self.base_url + '{}/'.format(response.data['id']), to_post)
        self.assertEquals(Client.objects.get(id=response.data['id']).name, to_post['name'])
        self.assertTrue(clients == Client.objects.count())
