from django.test import TestCase
from backend.api.tests import example_data as ed
from backend.recordmanagement.models import EncryptedClient


class ExampleDataTestCase(TestCase):
    def setUp(self) -> None:
        ed.create_fixtures()
        self.rlc = ed.create_rlc()
        self.dummy = ed.create_dummy_users(self.rlc)[0]
        self.rlc_public_key = self.rlc.get_public_key()
        self.dummy_private_key = self.dummy.get_private_key('qwe123')

    def test_create(self):
        clients = ed.create_clients(self.rlc)
        users = ed.create_users(self.rlc)
        ed.create_inactive_user(self.rlc)
        ed.create_groups(self.rlc, self.dummy, users)
        ed.create_records(clients, users, self.rlc)
        ed.create_admin_group(self.rlc, self.dummy)
        ed.create_informative_record(self.dummy, clients, users, self.rlc)

    def test_encrypt_and_decrypt_field(self):
        ed.create_clients(self.rlc)
        client = EncryptedClient.objects.first()
        client.decrypt(self.dummy.get_rlcs_private_key(self.dummy_private_key))
        note = client.note
        client.encrypt(self.rlc_public_key)
        client.decrypt(self.dummy.get_rlcs_private_key(self.dummy_private_key))
        self.assertEqual(note, client.note)

    def test_error_on_save_unencrypted(self):
        ed.create_clients(self.rlc)
        client = EncryptedClient.objects.first()
        client.decrypt(self.dummy.get_rlcs_private_key(self.dummy_private_key))
        with self.assertRaises(ValueError):
            client.save()

    def test_decrypt_client(self):
        ed.create_clients(self.rlc)
        client = EncryptedClient.objects.first()
        client.decrypt(self.dummy.get_rlcs_private_key(self.dummy_private_key))
        same_client = EncryptedClient.objects.get(pk=client.pk)
        same_client.decrypt(self.dummy.get_rlcs_private_key(self.dummy_private_key))
        self.assertEqual(client.note, same_client.note)
