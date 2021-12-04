from rest_framework.test import APIRequestFactory, force_authenticate
from django.test import TestCase


class RecordViewSetsWorking(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.rlc = Rlc.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(email='test@test.de', name='Dummy 1', rlc=self.rlc)
        self.user.set_password('test')
        self.user.save()
        self.rlc_user = RlcUser.objects.create(user=self.user, email_confirmed=True, accepted=True)
        self.another_user = UserProfile.objects.create(email='test_new@test.de', name='Dummy 2', rlc=self.rlc)
        self.another_user.set_password('test')
        self.another_user.save()
        self.another_rlc_user = RlcUser.objects.create(user=self.another_user, email_confirmed=True, accepted=True)
        self.rlc.generate_keys()
        self.private_key = bytes(self.user.encryption_keys.private_key).decode('utf-8')
        self.create_permissions()
