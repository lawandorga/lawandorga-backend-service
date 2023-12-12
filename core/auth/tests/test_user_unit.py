from django.conf import settings
from django.test import TestCase

from core.auth.domain.user_key import UserKey
from core.data_sheets.fixtures import create_default_record_template
from core.data_sheets.models import DataSheet, DataSheetEncryptionNew, DataSheetTemplate
from core.models import Org, OrgUser, UserProfile
from core.seedwork.encryption import AESEncryption


class UserUnitUserBase:
    def setUp(self):
        self.rlc = Org.objects.create(name="Test RLC")
        self.user1, self.rlc_user1 = self.create_user(
            "dummy@law-orga.de", "Dummy", settings.DUMMY_USER_PASSWORD
        )
        self.user2, self.rlc_user2 = self.create_user(
            "tester@law-orga.de", "Tester", settings.DUMMY_USER_PASSWORD
        )
        self.rlc.generate_keys()
        self.user1 = self.get_user(self.user1.pk)
        self.user2 = self.get_user(self.user2.pk)
        self.private_key1 = (
            UserKey.create_from_dict(self.user1.rlc_user.key)
            .decrypt_self(settings.DUMMY_USER_PASSWORD)
            .key.get_private_key()
            .decode("utf-8")
        )
        self.private_key2 = (
            UserKey.create_from_dict(self.user2.rlc_user.key)
            .decrypt_self(settings.DUMMY_USER_PASSWORD)
            .key.get_private_key()
            .decode("utf-8")
        )

        create_default_record_template(self.rlc)
        self.template = DataSheetTemplate.objects.filter(rlc=self.rlc).first()

    def get_user(self, pk):
        return UserProfile.objects.get(pk=pk)

    def create_user(self, email, name, password):
        user = UserProfile.objects.create(email=email, name=name)
        user.set_password(password)
        user.save()
        rlc_user = OrgUser(user=user, email_confirmed=True, accepted=True, org=self.rlc)
        rlc_user.generate_keys(password)
        rlc_user.save()
        return user, rlc_user


class UserUnitTests(UserUnitUserBase, TestCase):
    def generate_record_with_keys_for_users(self, users):
        record = DataSheet.objects.create(template=self.template)
        key = AESEncryption.generate_secure_key()
        for user in users:
            enc = DataSheetEncryptionNew(record=record, key=key, user=user.rlc_user)
            enc.encrypt(user.get_public_key())
            enc.save()
        return record

    def test_generate_keys_for_user_works_with_unlocking_user_having_the_keys(self):
        record = self.generate_record_with_keys_for_users([self.user1, self.user2])
        DataSheetEncryptionNew.objects.filter(user=self.user2.rlc_user).update(
            correct=False
        )
        self.user2.set_password("pass12345")
        self.user2.save()
        rlc_user = self.user2.rlc_user
        rlc_user.delete_keys()
        rlc_user.generate_keys("pass12345")
        rlc_user.save()
        private_key = (
            UserKey.create_from_dict(self.user2.rlc_user.key)
            .decrypt_self("pass12345")
            .key.get_private_key()
            .decode("utf-8")
        )
        success = self.user1.generate_keys_for_user(
            self.private_key1, UserProfile.objects.get(pk=self.user2.pk)
        )
        assert success is True
        enc = DataSheetEncryptionNew.objects.get(
            record=record, user=self.user2.rlc_user
        )
        enc.decrypt(private_key_user=private_key)

    def test_generate_keys_for_user_works_with_unlocking_user_not_having_the_keys(self):
        record = self.generate_record_with_keys_for_users([self.user2])
        # set all of those keys as incorrect
        DataSheetEncryptionNew.objects.filter(user=self.user2.rlc_user).update(
            correct=False
        )

        self.user2.rlc_user.delete_keys()
        self.user2.rlc_user.generate_keys("pass1234")
        self.user2.rlc_user.save()
        self.user2.set_password("pass1234")
        self.user2.save()
        private_key = (
            UserKey.create_from_dict(self.user2.rlc_user.key)
            .decrypt_self("pass1234")
            .key.get_private_key()
            .decode("utf-8")
        )

        success = self.user1.generate_keys_for_user(
            self.private_key1, UserProfile.objects.get(pk=self.user2.pk)
        )
        assert success is False
        enc = DataSheetEncryptionNew.objects.get(
            record=record, user=self.user2.rlc_user
        )
        with self.assertRaises(Exception):
            enc.decrypt(private_key_user=private_key)
