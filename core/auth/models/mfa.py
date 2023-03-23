from typing import Callable
from uuid import uuid4
from django.db import models
import pyotp
import urllib.parse
from core.auth.models.org_user import RlcUser
from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.symmetric_key import EncryptedSymmetricKey, SymmetricKey


class MultiFactorAuthenticationSecret(models.Model):
    @staticmethod
    def create(user: RlcUser, generator=pyotp.random_base32) -> "MultiFactorAuthenticationSecret":
        mfa = MultiFactorAuthenticationSecret(user=user)
        mfa.generate_secret(generator)
        return mfa

    uuid = models.UUIDField(default=uuid4, unique=True, db_index=True)
    user = models.OneToOneField(RlcUser, related_name='mfa_secret', on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)
    secret = models.JSONField()
    key = models.JSONField()

    class Meta:
        verbose_name = "MultiFactorAuthenticationSecret"
        verbose_name_plural = "MultiFactorAuthenticationSecrets"

    def __str__(self):
        return "multiFactorAuthenticationSecret: {}; user: {};".format(self.uuid, self.user.email)

    @property
    def url(self) -> str:
        totp = pyotp.totp.TOTP(self.get_secret())
        uri = totp.provisioning_uri(name=self.user.email, issuer_name="Law&Orga", image="https://backend.law-orga.de/static/logo256blue.png")
        encoded_uri = urllib.parse.quote(uri)
        google_uri = "https://chart.apis.google.com/chart?cht=qr&chs=250x250&chl={}"
        return google_uri.format(encoded_uri)

    def generate_secret(self, generator: Callable[..., str]):
        if self.secret is not None:
            raise ValueError("This mfa already has a secret.")
        self.__generate_key()
        secret = generator()
        box = OpenBox(data=secret.encode('utf-8'))
        key = self.__get_key()
        locked = key.lock(box)
        self.secret = locked.as_dict()

    def __get_key(self) -> SymmetricKey:
        enc_key = EncryptedSymmetricKey.create_from_dict(self.key)
        unlock_key = self.user.get_decryption_key()
        key = enc_key.decrypt(unlock_key)
        return key

    def __generate_key(self):
        key = SymmetricKey.generate()
        lock_key = self.user.get_encryption_key()
        enc_key = EncryptedSymmetricKey.create(key, lock_key)
        self.key = enc_key.as_dict()

    def get_code(self, totp_class=pyotp.TOTP) -> str:
        secret = self.get_secret()
        totp = totp_class(secret)
        return totp.now()

    def get_secret(self) -> str:
        unlock_key = self.user.get_decryption_key()
        enc_key = EncryptedSymmetricKey.create_from_dict(self.key)
        key = enc_key.decrypt(unlock_key)
        enc_secret = LockedBox.create_from_dict(self.secret)
        secret = key.unlock(enc_secret)
        return secret.decode('utf-8')

    def enable(self):
        self.enabled = True
