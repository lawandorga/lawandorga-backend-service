from django.test import Client, TestCase

from apps.core.models import Org, OrgEncryption, Permission
from apps.core.records.models import RecordTemplate
from apps.core.static import get_all_permission_strings
from apps.static import test_helpers as data


class TestRlcUser(TestCase):
    def setUp(self):
        self.rlc = Org.objects.create(name="Test RLC")
        self.user_1 = data.create_rlc_user(rlc=self.rlc)
        # self.user_2 = data.create_rlc_user(email="dummy2@law-orga.de", rlc=self.rlc)
        # self.user_3 = data.create_rlc_user(email="dummy3@law-orga.de", rlc=self.rlc)
        self.rlc.generate_keys()
        self.create_permissions()
        self.template = RecordTemplate.objects.create(
            rlc=self.rlc, name="Record Template"
        )
        self.record_1 = data.create_record(
            template=self.template, users=[self.user_1["user"]]
        )
        # self.record_2 = data.create_record(
        #     template=self.template, users=[self.user_1["user"], self.user_2["user"]]
        # )
        self.client = Client()
        self.client.login(**self.user_1)

    def create_permissions(self):
        for perm in get_all_permission_strings():
            Permission.objects.create(name=perm)

    def get_user_rlc_keys(self, user_obj):
        keys = OrgEncryption.objects.get(pk=user_obj["user"].users_rlc_keys.first().pk)
        return keys

    def get_user_record_key(self, record_obj, user_obj):
        key = record_obj["record"].encryptions.get(user=user_obj["user"])
        return key

    def test_unlock_fails(self):
        # setup
        key = self.get_user_record_key(self.record_1, self.user_1)
        key.correct = False
        key.save()
        # check
        c = Client()
        c.login(**self.user_1)
        response = c.post("/api/rlc_users/unlock_self/")
        assert response.status_code == 400

    def test_unlock_works(self):
        # setup
        rlc_user = self.user_1["rlc_user"]
        rlc_user.locked = True
        rlc_user.encrypt(password=self.user_1["password"])
        rlc_user.save()
        # check
        c = Client()
        c.login(**self.user_1)
        response = c.post("/api/rlc_users/unlock_self/")
        response_data = response.json()
        assert response_data["locked"] is False
