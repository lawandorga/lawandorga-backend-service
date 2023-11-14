from django.test import Client, TestCase

from core.models import Org, OrgEncryption
from core.seedwork import test_helpers as data


class TestRlcUser(TestCase):
    def setUp(self):
        self.rlc = Org.objects.create(name="Test RLC")
        self.user_1 = data.create_org_user(rlc=self.rlc)
        self.rlc.generate_keys()
        self.record_1 = data.create_data_sheet(users=[self.user_1["user"]])
        self.client = Client()
        self.client.login(**self.user_1)

    def get_user_rlc_keys(self, user_obj):
        keys = OrgEncryption.objects.get(pk=user_obj["user"].users_rlc_keys.first().pk)
        return keys

    def get_user_record_key(self, record_obj, user_obj):
        key = record_obj["record"].encryptions.get(user=user_obj["rlc_user"])
        return key

    def test_unlock_fails(self):
        # setup
        key = OrgEncryption.objects.get(user=self.user_1["user"])
        key.correct = False
        key.encrypted_key = b""
        key.save()
        # check
        response = self.client.post("/api/rlc_users/unlock_self/")
        assert response.status_code == 400

    def test_unlock_works(self):
        # setup
        rlc_user = self.user_1["rlc_user"]
        rlc_user.locked = True
        rlc_user.save()
        # check
        response = self.client.post("/api/rlc_users/unlock_self/")
        response_data = response.json()
        assert response_data["locked"] is False
