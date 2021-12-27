from apps.api.tests import example_data as ed
from django.test import TestCase


class ExampleDataTestCase(TestCase):
    def test_example_data_create_works(self):
        ed.create()
    # def setUp(self) -> None:
    #     dummy_password = "qwe123"
    #     # fixtures
    #     ed.create_fixtures()
    #     # dummy
    #     self.rlc, self.another_rlc = ed.create_rlcs()
    #     self.dummy = ed.create_dummy_users(self.rlc)[0]
    #     # keys
    #     self.dummy_private_key = self.dummy.get_private_key(dummy_password)
    #     self.rlc_public_key = self.rlc.get_public_key()
    #     self.rlc_private_key = self.rlc.get_private_key(self.dummy, self.dummy_private_key)
    #     # data
    #     self.users = ed.create_users(self.rlc, self.another_rlc)
    #     self.inactive_user = ed.create_inactive_user(self.rlc)
    #     self.groups = ed.create_groups(self.rlc, self.dummy, self.users)
    #     self.records = ed.create_records(self.users, self.rlc)
    #     self.admin_group = ed.create_admin_group(self.rlc, self.dummy)
    #     self.informative_record = ed.create_informative_record(self.dummy, dummy_password, self.users, self.rlc)
    #
    # def test_record_message_error_on_save_unecrypted(self):
    #     message = self.informative_record.messages.first()
    #     message.decrypt(self.dummy, self.dummy_private_key)
    #     with self.assertRaises(ValueError):
    #         message.save()
    #
    # def test_record_message_encrypt_and_decrypt(self):
    #     message = self.informative_record.messages.first()
    #     message.decrypt(self.dummy, self.dummy_private_key)
    #     first_message = message.message
    #     message.encrypt(self.dummy, self.dummy_private_key)
    #     message.decrypt(self.dummy, self.dummy_private_key)
    #     second_message = message.message
    #     self.assertEqual(first_message, second_message)
