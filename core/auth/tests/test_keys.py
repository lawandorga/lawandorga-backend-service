from django.test import Client, TestCase

from core.auth.use_cases.keys import check_keys
from core.data_sheets.models import DataSheetTemplate
from core.models import Org, OrgEncryption
from core.seedwork import test_helpers as data
from core.seedwork.encryption import RSAEncryption


class TestUserKeys(TestCase):
    def setUp(self):
        self.rlc = Org.objects.create(name="Test RLC")
        self.user_1 = data.create_org_user(rlc=self.rlc)
        self.user_2 = data.create_org_user(email="dummy2@law-orga.de", rlc=self.rlc)
        self.user_3 = data.create_org_user(email="dummy3@law-orga.de", rlc=self.rlc)
        self.rlc.generate_keys()
        self.template = DataSheetTemplate.objects.create(
            rlc=self.rlc, name="Record Template"
        )
        self.record_1 = data.create_data_sheet(
            template=self.template, users=[self.user_1["user"], self.user_2["user"]]
        )
        self.record_2 = data.create_data_sheet(
            template=self.template, users=[self.user_1["user"], self.user_2["user"]]
        )
        self.client = Client()
        self.client.login(**self.user_1)

    def get_user_rlc_keys(self, user_obj):
        keys = OrgEncryption.objects.get(pk=user_obj["user"].users_rlc_keys.first().pk)
        return keys

    def get_user_record_key(self, record_obj, user_obj):
        key = record_obj["record"].encryptions.get(user=user_obj["rlc_user"])
        return key

    def test_rlc_key_check(self):
        objs = self.user_1["rlc_user"].test_keys()
        [obj.save() for obj in objs]
        assert self.get_user_rlc_keys(self.user_1).correct
        keys = self.get_user_rlc_keys(self.user_1)
        keys.encrypted_key = b"1234"
        private, public = RSAEncryption.generate_keys()
        keys.encrypt(public)
        keys.save()
        objs = self.user_1["rlc_user"].test_keys()
        [obj.save() for obj in objs]
        assert not self.get_user_rlc_keys(self.user_1).correct
        keys = self.get_user_rlc_keys(self.user_1)
        keys.encrypted_key = b"1234"
        keys.encrypt(self.user_1["public_key"])
        keys.save()
        objs = self.user_1["rlc_user"].test_keys()
        [obj.save() for obj in objs]
        assert self.get_user_rlc_keys(self.user_1).correct

    def test_list_keys(self):
        c = Client()
        c.login(**self.user_1)
        c.get("/api/keys/")

    def test_keys_test(self):
        check_keys(self.user_1["rlc_user"])
