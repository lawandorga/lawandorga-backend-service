from apps.recordmanagement.models import Record, RecordTemplate, RecordEncryptionNew
from apps.static.encryption import RSAEncryption, AESEncryption
from apps.api.models import UserProfile, RlcUser, Rlc, Permission, UsersRlcKeys
from apps.api.static import get_all_permission_strings
from django.test import TestCase
from django.conf import settings


class TestUserKeys(TestCase):
    def setUp(self):
        self.rlc = Rlc.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(email='dummy@law-orga.de', name='Dummy 1', rlc=self.rlc)
        self.user.set_password(settings.DUMMY_USER_PASSWORD)
        self.user.save()
        self.rlc_user = RlcUser.objects.create(user=self.user, email_confirmed=True, accepted=True)
        self.rlc.generate_keys()
        self.private_key = bytes(self.user.encryption_keys.private_key).decode('utf-8')
        self.create_permissions()
        # record keys
        self.template = RecordTemplate.objects.create(rlc=self.rlc, name='Record Template')
        self.record = Record.objects.create(template=self.template)
        self.aes_key_record = AESEncryption.generate_secure_key()
        self.public_key_user = self.user.get_public_key()
        self.encryption = RecordEncryptionNew(record=self.record, user=self.user, key=self.aes_key_record)
        self.encryption.encrypt(public_key_user=self.public_key_user)
        self.encryption.save()

    def create_permissions(self):
        for perm in get_all_permission_strings():
            Permission.objects.create(name=perm)

    def get_user_rlc_keys(self):
        keys = UsersRlcKeys.objects.get(pk=self.user.users_rlc_keys.first().pk)
        return keys

    def get_user_record_key(self):
        key = RecordEncryptionNew.objects.get(pk=self.encryption.pk)
        return key

    def test_rlc_key_check(self):
        self.get_user_rlc_keys().test(self.private_key)
        assert self.get_user_rlc_keys().correct
        keys = self.get_user_rlc_keys()
        keys.encrypted_key = b'1234'
        private, public = RSAEncryption.generate_keys()
        keys.encrypt(public)
        keys.save()
        self.get_user_rlc_keys().test(self.private_key)
        assert not self.get_user_rlc_keys().correct
        keys = self.get_user_rlc_keys()
        keys.encrypted_key = b'1234'
        keys.encrypt(self.public_key_user)
        keys.save()
        self.get_user_rlc_keys().test(self.private_key)
        assert self.get_user_rlc_keys().correct

    def test_record_key_check(self):
        self.get_user_record_key().test(self.private_key)
        assert self.get_user_rlc_keys().correct
        keys = self.get_user_record_key()
        keys.key = b'1234'
        private, public = RSAEncryption.generate_keys()
        keys.encrypt(public)
        keys.save()
        self.get_user_record_key().test(self.private_key)
        assert not self.get_user_record_key().correct
        keys = self.get_user_record_key()
        keys.key = b'1234'
        keys.encrypt(self.public_key_user)
        keys.save()
        self.get_user_record_key().test(self.private_key)
        assert self.get_user_rlc_keys().correct
