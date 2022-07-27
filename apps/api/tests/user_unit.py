from django.conf import settings
from django.test import TestCase

from apps.api.models import Permission, Rlc, RlcUser, UserProfile
from apps.api.static import get_all_permission_strings
from apps.recordmanagement.fixtures import create_default_record_template
from apps.recordmanagement.models import Record, RecordEncryptionNew, RecordTemplate
from apps.static.encryption import AESEncryption


class UserBase:
    def setUp(self):
        self.rlc = Rlc.objects.create(name="Test RLC")
        self.user1, self.rlc_user1 = self.create_user(
            "dummy@law-orga.de", "Dummy", settings.DUMMY_USER_PASSWORD
        )
        self.user2, self.rlc_user2 = self.create_user(
            "tester@law-orga.de", "Tester", "pass1234"
        )
        self.rlc.generate_keys()
        self.user1 = self.get_user(self.user1.pk)
        self.user2 = self.get_user(self.user2.pk)
        self.private_key1 = self.user1.get_private_key(settings.DUMMY_USER_PASSWORD)
        self.private_key2 = self.user2.get_private_key("pass1234")

        self.create_permissions()
        create_default_record_template(self.rlc)
        self.template = RecordTemplate.objects.filter(rlc=self.rlc).first()

    def get_user(self, pk):
        return UserProfile.objects.get(pk=pk)

    def create_user(self, email, name, password):
        user = UserProfile.objects.create(email=email, name=name, rlc=self.rlc)
        user.set_password(password)
        user.save()
        rlc_user = RlcUser.objects.create(
            user=user, email_confirmed=True, accepted=True
        )
        return user, rlc_user

    def create_permissions(self):
        for perm in get_all_permission_strings():
            Permission.objects.create(name=perm)


class UserUnitTests(UserBase, TestCase):
    def generate_record_with_keys_for_users(self, users):
        record = Record.objects.create(template=self.template)
        key = AESEncryption.generate_secure_key()
        for user in users:
            enc = RecordEncryptionNew(record=record, key=key, user=user)
            enc.encrypt(user.get_public_key())
            enc.save()
        return record

    def test_generate_keys_for_user_works_with_unlocking_user_having_the_keys(self):
        record = self.generate_record_with_keys_for_users([self.user1, self.user2])
        RecordEncryptionNew.objects.filter(user=self.user2).update(correct=False)
        self.user2.set_password("pass12345")
        self.user2.save()
        self.user2.rlc_user.delete_keys()
        private_key = UserProfile.objects.get(pk=self.user2.pk).get_private_key(
            "pass12345"
        )
        success = self.user1.generate_keys_for_user(
            self.private_key1, UserProfile.objects.get(pk=self.user2.pk)
        )
        assert success is True
        enc = RecordEncryptionNew.objects.get(record=record, user=self.user2)
        enc.decrypt(private_key_user=private_key)

    def test_generate_keys_for_user_works_with_unlocking_user_not_having_the_keys(self):
        record = self.generate_record_with_keys_for_users([self.user2])
        # set all of those keys as incorrect
        RecordEncryptionNew.objects.filter(user=self.user2).update(correct=False)

        self.user2.set_password("pass12345")
        self.user2.save()
        self.user2.rlc_user.delete_keys()
        private_key = UserProfile.objects.get(pk=self.user2.pk).get_private_key(
            "pass12345"
        )
        success = self.user1.generate_keys_for_user(
            self.private_key1, UserProfile.objects.get(pk=self.user2.pk)
        )
        assert success is False
        enc = RecordEncryptionNew.objects.get(record=record, user=self.user2)
        with self.assertRaises(ValueError):
            enc.decrypt(private_key_user=private_key)
