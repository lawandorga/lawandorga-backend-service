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

from django.test import TransactionTestCase
from rest_framework.response import Response
from rest_framework.test import APIClient

from backend.api import models as api_models
from backend.api.models.notification import NotificationEvent, NotificationEventSubject
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.recordmanagement import models as record_models


class NotificationTest(TransactionTestCase):
    def setUp(self):
        self.base_fixtures = CreateFixtures.create_base_fixtures()
        users: [api_models.UserProfile] = [self.base_fixtures['users'][0]['user'],
                                           self.base_fixtures['users'][1]['user'],
                                           self.base_fixtures['users'][2]['user']]
        self.record_fixtures = CreateFixtures.create_record_base_fixtures(rlc=self.base_fixtures['rlc'], users=users)

    def test_record_message_notification(self):
        record: record_models.EncryptedRecord = self.record_fixtures['records'][0]['record']
        before = api_models.Notification.objects.all().count()

        # from fixtures
        private_key: bytes = self.base_fixtures['users'][0]['private']
        client: APIClient = self.base_fixtures['users'][0]['client']

        # post new record message
        client.post('/api/records/e_record/' + str(record.id) + '/messages', {'message': 'secret message'},
                    **{'HTTP_PRIVATE_KEY': private_key})

        # 2 because record send notification to 2 other users (1 causes it)
        self.assertEqual(before + 2, api_models.Notification.objects.all().count())
        notification_for_user_1: api_models.Notification = api_models.Notification.objects.filter(
            user=self.base_fixtures['users'][1]['user']).first()
        self.assertTrue(notification_for_user_1 is not None)
        self.assertEqual(notification_for_user_1.source_user, self.base_fixtures['users'][0]['user'])
        self.assertEqual(notification_for_user_1.read, False)
        self.assertEqual(notification_for_user_1.ref_id, str(record.id))
        self.assertEqual(notification_for_user_1.ref_text, str(record.record_token))

    def test_login_notifications(self):
        NotificationTest.generate_notifications(self.base_fixtures['users'][0]['user'],
                                                self.base_fixtures['users'][1]['user'], 104)
        notification: api_models.Notification = api_models.Notification.objects.filter(user__email='user1@law-orga.de').first()
        notification.read = True
        notification.save()

        login_response: Response = APIClient().post('/api/login/',
                                                    {'username': 'user1@law-orga.de', 'password': 'qwe123'})
        self.assertEqual(200, login_response.status_code)
        self.assertIn('notifications', login_response.data)
        self.assertEqual(103, login_response.data['notifications'])

    def test_get_notifications(self):
        generated_notifications: [api_models.Notification] = NotificationTest.generate_notifications(
            self.base_fixtures['users'][0]['user'],
            self.base_fixtures['users'][1]['user'], 104)
        NotificationTest.generate_notifications(self.base_fixtures['users'][1]['user'],
                                                self.base_fixtures['users'][0]['user'], 20)
        client: APIClient = self.base_fixtures['users'][0]['client']
        # response: Response = client.get('/api/my_notifications/')
        response: Response = client.get('/api/notifications/')
        self.assertIn('count', response.data)
        self.assertEqual(104, response.data['count'])
        self.assertIn('results', response.data)
        notifications_from_response = response.data['results']
        self.assertEqual(100, notifications_from_response.__len__())
        self.assertEqual(generated_notifications[0].id, notifications_from_response[0]['id'])
        self.assertEqual(generated_notifications[20].id, notifications_from_response[20]['id'])
        self.assertEqual(generated_notifications[99].id, notifications_from_response[99]['id'])

    def test_update_notification(self):
        generated_notifications: [api_models.Notification] = NotificationTest.generate_notifications(
            self.base_fixtures['users'][0]['user'],
            self.base_fixtures['users'][1]['user'], 30)
        client: APIClient = self.base_fixtures['users'][0]['client']

        # read
        response_read_true: Response = client.patch('/api/notifications/' + str(generated_notifications[0].id) + '/',
                                                    {'read': True})
        self.assertEqual(200, response_read_true.status_code)
        self.assertTrue(api_models.Notification.objects.get(id=generated_notifications[0].id).read)

        # unread
        response_read_false: Response = client.patch('/api/notifications/' + str(generated_notifications[0].id) + '/',
                                                     {'read': False})
        self.assertEqual(200, response_read_false.status_code)
        self.assertFalse(api_models.Notification.objects.get(id=generated_notifications[0].id).read)

        # not read
        response: Response = client.patch('/api/notifications/' + str(generated_notifications[0].id) + '/',
                                          {'ref_id': "hello there"})
        self.assertEqual(400, response.status_code)

        response: Response = client.patch('/api/notifications/' + str(generated_notifications[0].id) + '/',
                                          {'ref_id': "hello there", 'read': True})
        self.assertEqual(400, response.status_code)

        other_client: APIClient = self.base_fixtures['users'][1]['client']
        response: Response = other_client.patch('/api/notifications/' + str(generated_notifications[0].id) + '/',
                                                {'read': True})
        self.assertEqual(403, response.status_code)

        response: Response = client.patch('/api/notifications/' + str(generated_notifications[0].id) + '123/',
                                          {'read': True})
        self.assertEqual(400, response.status_code)

    def test_delete_notification(self):
        pass

    @staticmethod
    def get_created(notification):
        return notification.created

    @staticmethod
    def generate_notifications(user: api_models.UserProfile, source_user: api_models.UserProfile,
                               number_of_notifications: int):
        """
        generates notifications, each time the same
        only even numbers for number_of_notifications
        return newest notifications
        :param user:
        :param source_user:
        :param number_of_notifications: number of created notification, even number because half 'new' half 'older' notification
        :return: all generated notifications, newest first
        """
        import datetime
        from django.utils import timezone
        notifications = []
        for i in range(int(number_of_notifications / 2)):
            notification = api_models.Notification(user=user, source_user=source_user,
                                                   event_subject=NotificationEventSubject.RECORD,
                                                   event=NotificationEvent.UPDATED, ref_id="123", ref_text="AZ 123/12")
            notification.save()
            notification.created = timezone.now() - datetime.timedelta(hours=i)
            notification.save()
            notifications.append(notification)

            notification2 = api_models.Notification(user=user, source_user=source_user,
                                                    event_subject=NotificationEventSubject.RECORD,
                                                    event=NotificationEvent.UPDATED, ref_id="123", ref_text="AZ 123/12")
            notification2.save()
            notification2.created = timezone.now() - datetime.timedelta(days=i)
            notification2.save()
            notifications.append(notification2)
        notifications.sort(key=NotificationTest.get_created, reverse=True)
        return notifications
