from django.test import Client, TestCase

from apps.core.models import Org, OrgEncryption, Permission
from apps.core.records.models import RecordEncryptionNew, RecordTemplate
from apps.core.static import get_all_permission_strings
from apps.seedwork import test_helpers as data
from apps.seedwork.encryption import RSAEncryption


class TestUserKeys(TestCase):
    def setUp(self):
        self.rlc = Org.objects.create(name="Test RLC")
        self.user_1 = data.create_rlc_user(rlc=self.rlc)
        self.user_2 = data.create_rlc_user(email="dummy2@law-orga.de", rlc=self.rlc)
        self.user_3 = data.create_rlc_user(email="dummy3@law-orga.de", rlc=self.rlc)
        self.rlc.generate_keys()
        self.create_permissions()
        self.template = RecordTemplate.objects.create(
            rlc=self.rlc, name="Record Template"
        )
        self.record_1 = data.create_record(
            template=self.template, users=[self.user_1["user"], self.user_2["user"]]
        )
        self.record_2 = data.create_record(
            template=self.template, users=[self.user_1["user"], self.user_2["user"]]
        )
        self.client = Client()
        self.client.login(**self.user_1)

    def create_permissions(self):
        for perm in get_all_permission_strings():
            Permission.objects.create(name=perm)

    def get_user_rlc_keys(self, user_obj):
        keys = OrgEncryption.objects.get(pk=user_obj["user"].users_rlc_keys.first().pk)
        return keys

    def get_user_record_key(self, record_obj, user_obj):
        key = record_obj["record"].encryptions.get(user=user_obj["rlc_user"])
        return key

    def test_rlc_key_check(self):
        self.get_user_rlc_keys(self.user_1).test(self.user_1["private_key"])
        assert self.get_user_rlc_keys(self.user_1).correct
        keys = self.get_user_rlc_keys(self.user_1)
        keys.encrypted_key = b"1234"
        private, public = RSAEncryption.generate_keys()
        keys.encrypt(public)
        keys.save()
        self.get_user_rlc_keys(self.user_1).test(self.user_1["private_key"])
        assert not self.get_user_rlc_keys(self.user_1).correct
        keys = self.get_user_rlc_keys(self.user_1)
        keys.encrypted_key = b"1234"
        keys.encrypt(self.user_1["public_key"])
        keys.save()
        self.get_user_rlc_keys(self.user_1).test(self.user_1["private_key"])
        assert self.get_user_rlc_keys(self.user_1).correct

    def test_record_key_check(self):
        self.get_user_record_key(self.record_1, self.user_1).test(
            self.user_1["private_key"]
        )
        assert self.get_user_rlc_keys(self.user_1).correct
        keys = self.get_user_record_key(self.record_1, self.user_1)
        keys.key = b"1234"
        private, public = RSAEncryption.generate_keys()
        keys.encrypt(public)
        keys.save()
        self.get_user_record_key(self.record_1, self.user_1).test(
            self.user_1["private_key"]
        )
        assert not self.get_user_record_key(self.record_1, self.user_1).correct
        keys = self.get_user_record_key(self.record_1, self.user_1)
        keys.key = b"1234"
        keys.encrypt(self.user_1["public_key"])
        keys.save()
        self.get_user_record_key(self.record_1, self.user_1).test(
            self.user_1["private_key"]
        )
        assert self.get_user_record_key(self.record_1, self.user_1).correct

    def test_list_keys(self):
        c = Client()
        c.login(**self.user_1)
        response = c.get("/api/keys/")
        response_data = response.json()
        assert RecordEncryptionNew.objects.filter(
            user=self.user_1["rlc_user"]
        ).count() + 1 == len(response_data)

    def test_delete_key(self):
        c = Client()
        c.login(**self.user_1)
        key_id = self.get_user_record_key(self.record_1, self.user_1).pk
        response = c.delete("/api/keys/{}/".format(key_id))
        print(response.json())
        assert response.status_code == 400
        response = c.delete("/api/keys/999999/")
        assert response.status_code == 400
        keys = self.get_user_record_key(self.record_1, self.user_1)
        keys.key = b"1234"
        private, public = RSAEncryption.generate_keys()
        keys.encrypt(public)
        keys.save()
        response = c.delete("/api/keys/{}/".format(key_id))
        assert response.status_code == 400
        encryption = RecordEncryptionNew(
            record=self.record_1["record"],
            user=self.user_3["rlc_user"],
            key=self.record_1["aes_key"],
        )
        encryption.encrypt(public_key_user=self.user_3["public_key"])
        encryption.save()
        response = c.delete("/api/keys/{}/".format(key_id))
        assert response.status_code == 400
        keys.test(self.user_1["private_key"])
        response = c.delete("/api/keys/{}/".format(key_id))
        assert response.status_code == 200

    def test_keys_test(self):
        response = self.client.post("/api/keys/test/")
        assert response.status_code == 200
