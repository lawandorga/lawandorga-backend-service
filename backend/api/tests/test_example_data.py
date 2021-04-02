from django.test import TestCase
from backend.api.tests import example_data as ed
from backend.recordmanagement.models import EncryptedRecord
from backend.recordmanagement.models.encrypted_client import EncryptedClient


class ExampleDataTestCase(TestCase):
    def setUp(self) -> None:
        dummy_password = "qwe123"
        # fixtures
        ed.create_fixtures()
        # dummy
        self.rlc = ed.create_rlc()
        self.dummy = ed.create_dummy_users(self.rlc)[0]
        # keys
        self.dummy_private_key = self.dummy.get_private_key(dummy_password)
        self.rlc_public_key = self.rlc.get_public_key()
        self.rlc_private_key = self.rlc.get_private_key(
            self.dummy, self.dummy_private_key
        )
        # data
        self.clients = ed.create_clients(self.rlc)
        self.users = ed.create_users(self.rlc)
        self.inactive_user = ed.create_inactive_user(self.rlc)
        self.groups = ed.create_groups(self.rlc, self.dummy, self.users)
        self.records = ed.create_records(self.clients, self.users, self.rlc)
        self.admin_group = ed.create_admin_group(self.rlc, self.dummy)
        self.informative_record = ed.create_informative_record(
            self.dummy, dummy_password, self.clients, self.users, self.rlc
        )

    def test_client_encrypt_and_decrypt_field(self):
        ed.create_clients(self.rlc)
        client = EncryptedClient.objects.first()
        client.decrypt(self.dummy.get_rlcs_private_key(self.dummy_private_key))
        note = client.note
        client.encrypt(self.rlc_public_key)
        client.decrypt(self.dummy.get_rlcs_private_key(self.dummy_private_key))
        self.assertEqual(note, client.note)

    def test_client_error_on_save_unencrypted(self):
        client = self.clients[0]
        client.decrypt(self.dummy.get_rlcs_private_key(self.dummy_private_key))
        with self.assertRaises(ValueError):
            client.save()

    def test_client_decrypt(self):
        ed.create_clients(self.rlc)
        client = EncryptedClient.objects.first()
        client.decrypt(self.dummy.get_rlcs_private_key(self.dummy_private_key))
        same_client = EncryptedClient.objects.get(pk=client.pk)
        same_client.decrypt(self.dummy.get_rlcs_private_key(self.dummy_private_key))
        self.assertEqual(client.note, same_client.note)

    def test_record_error_on_save_unencrypted(self):
        client = self.clients[0]
        client.decrypt(self.rlc_private_key)
        with self.assertRaises(ValueError):
            client.save()

    def test_record_encrypt_and_decrypt(self):
        record1 = self.informative_record
        record2 = EncryptedRecord.objects.get(pk=record1.pk)
        self.assertNotEqual(record1.note, bytes())
        self.assertNotEqual(record2.note, bytes())
        self.assertEqual(record1.note, record2.note)
        record1.decrypt(self.dummy, self.dummy_private_key)
        record1.encrypt(self.dummy, self.dummy_private_key)
        record1.decrypt(self.dummy, self.dummy_private_key)
        record2.decrypt(self.dummy, self.dummy_private_key)
        self.assertEqual(record1.note, record2.note)

    def test_record_message_error_on_save_unecrypted(self):
        message = self.informative_record.messages.first()
        message.decrypt(self.dummy, self.dummy_private_key)
        with self.assertRaises(ValueError):
            message.save()

    def test_record_message_encrypt_and_decrypt(self):
        message = self.informative_record.messages.first()
        message.decrypt(self.dummy, self.dummy_private_key)
        first_message = message.message
        message.encrypt(self.dummy, self.dummy_private_key)
        message.decrypt(self.dummy, self.dummy_private_key)
        second_message = message.message
        self.assertEqual(first_message, second_message)
