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
from backend.recordmanagement.models import OriginCountry
from backend.api.tests.fixtures import CreateFixtures
from backend.api.tests.statics import StaticTestMethods
# TODO: test destroy


class OriginCountriesTests(TransactionTestCase):
    def setUp(self):
        self.client = StaticTestMethods.force_authentication()
        self.base_url = '/api/records/origin_countries/'

    def test_create_originCountry_success(self):
        self.assertTrue(OriginCountry.objects.count() == 0)
        response = self.client.post(self.base_url, {
            'name': 'Botswana',
            'state': 'ot'
        })
        all_after_saving = list(OriginCountry.objects.all())
        data = response.data
        # actual return
        self.assertEqual(data['clients'], [])
        self.assertEqual(data['name'], 'Botswana')
        self.assertEqual(data['state'], 'ot')
        # actual database
        self.assertEqual(all_after_saving[0].name, data['name'])
        self.assertEqual(all_after_saving[0].state, data['state'])
        self.assertEqual(all_after_saving[0].id, data['id'])
        self.assertTrue(response.status_code == 201)

    def test_create_originCountry_error_duplicate_name(self):
        to_save = {
            'name': 'Botswana',
            'state': 'ot'
        }
        # works the first time
        self.client.post(self.base_url, to_save)
        status_before_posting_second = list(OriginCountry.objects.all())
        response = self.client.post(self.base_url, to_save)
        self.assertEqual(response.status_code, 400)
        status_after_posting_second = list(OriginCountry.objects.all())
        self.assertEqual(status_after_posting_second,
                         status_before_posting_second)

    def test_create_originCountry_error_no_state(self):
        to_save = {
            'name': 'Botswana'
            # state missing
        }
        response = self.client.post(self.base_url, to_save)
        self.assertEqual(response.status_code, 400)

    def test_create_originCountry_error_not_existing_state(self):
        to_save = {
            'name': 'Botswana',
            'state': 'qq'
        }
        response = self.client.post(self.base_url, to_save)
        self.assertEqual(response.status_code, 400)

    def test_create_originCountry_error_state_too_long(self):
        to_save = {
            'name': 'Botswana',
            'state': 'safe country'
        }
        response = self.client.post(self.base_url, to_save)
        self.assertEqual(response.status_code, 400)

    def test_create_unauthenticated(self):
        client = APIClient()
        response = client.post(self.base_url, {
            'name': 'Botswana',
            'state': 'so'
        })
        self.assertEqual(response.status_code, 401)

    def test_create_multiple_originCountries(self):
        before = OriginCountry.objects.count()
        created = CreateFixtures.create_sample_countries()
        after = OriginCountry.objects.count()

        self.assertTrue(after == before + created.__len__())

    def test_edit_put_originCountry_success(self):
        CreateFixtures.create_sample_countries()
        countries = list(OriginCountry.objects.all())
        change_to = {
            'name': 'Deutschland',
            'state': 'st'
        }
        response = self.client.put(
            self.base_url+'{}/'.format(countries[0].id), change_to)
        countries_after = list(OriginCountry.objects.all())

        for i in range(1, countries.__len__()):
            self.assertEqual(countries[i], countries_after[i])
        self.assertTrue(response.status_code == 200)
        self.assertTrue(countries_after[0].name == change_to['name'])
        self.assertTrue(countries_after[0].state == change_to['state'])

    def test_edit_put_originCountry_error_wrong_state(self):
        CreateFixtures.create_sample_countries()
        countries = list(OriginCountry.objects.all())
        change_to = {
            'name': 'Deutschland',
            'state': 'so safe'
        }
        response = self.client.put(
            self.base_url+'{}/'.format(countries[0].id), change_to)
        self.assertEqual(response.status_code, 400)

    def test_edit_put_originCountry_error_state_missing(self):
        CreateFixtures.create_sample_countries()
        countries = list(OriginCountry.objects.all())
        change_to = {
            'name': 'Deutschland'
        }
        response = self.client.put(
            self.base_url+'{}/'.format(countries[0].id), change_to)
        self.assertEqual(response.status_code, 400)

    def test_edit_patch_originCountry_success(self):
        CreateFixtures.create_sample_countries()
        countries = list(OriginCountry.objects.all())
        change_to = {
            'name': 'Deutschland'
        }
        response = self.client.patch(
            self.base_url+'{}/'.format(countries[0].id), change_to)
        countries_after = list(OriginCountry.objects.all())

        for i in range(1, countries.__len__()):
            self.assertEqual(countries[i], countries_after[i])
        self.assertTrue(response.status_code == 200)
        self.assertTrue(countries_after[0].name == change_to['name'])
        self.assertTrue(countries_after[0].state == countries[0].state)

    def test_edit_patch_originCountry_error_wrong_state(self):
        CreateFixtures.create_sample_countries()
        countries = list(OriginCountry.objects.all())
        change_to = {
            'state': 'so safe'
        }
        response = self.client.put(
            self.base_url+'{}/'.format(countries[0].id), change_to)
        self.assertEqual(response.status_code, 400)

    def test_get_all_countries_success(self):
        CreateFixtures.create_sample_countries()
        response = self.client.get(self.base_url)
        countries = OriginCountry.objects.count()
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.data.__len__() == countries)

    def test_get_all_countries_error_unauthenticated(self):
        client = APIClient()
        response = client.get(self.base_url)
        self.assertTrue(response.status_code == 401)
