from django.core.management.base import BaseCommand

from core.auth.domain.user_key import UserKey
from core.auth.models import RlcUser
from core.folders.domain.value_objects.box import LockedBox
from core.folders.domain.value_objects.keys import AsymmetricKey, EncryptedAsymmetricKey


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = list(RlcUser.objects.all())
        for u in users:
            # todo: watch out for private keys that are not encrypted
            if u.public_key and u.private_key:
                if u.is_private_key_encrypted:
                    enc_key = None
                    enc_private_key = LockedBox(enc_data=u.private_key, key_origin="S1")
                    public_key = u.public_key.decode("utf-8")
                    origin = "A1"
                    key = EncryptedAsymmetricKey(
                        enc_key=enc_key,
                        enc_private_key=enc_private_key,
                        public_key=public_key,
                        origin=origin,
                    )
                    user_key = UserKey(key=key)
                    u.key = user_key.as_dict()
                else:
                    private_key = u.private_key.decode("utf-8")
                    public_key = u.public_key.decode("utf-8")
                    origin = "A1"
                    u.key = {
                        "private_key": private_key,
                        "public_key": public_key,
                        "origin": origin,
                    }
        RlcUser.objects.bulk_update(users, fields=["key"])
