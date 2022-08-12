from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from apps.core.static import PERMISSION_ADMIN_MANAGE_USERS
from apps.static.encryption import AESEncryption, RSAEncryption, EncryptedModelMixin


if TYPE_CHECKING:
    from apps.core.models.auth.user import UserProfile


class Rlc(EncryptedModelMixin, models.Model):
    FEDERAL_STATE_CHOICES = (
        ("BW", "Baden-Württemberg"),
        ("BY", "Bayern (Freistaat)"),
        ("BE", "Berlin"),
        ("BB", "Brandenburg"),
        ("HB", "Bremen (Hansestadt)"),
        ("HH", "Hamburg (Hansestadt)"),
        ("HE", "Hessen"),
        ("MV", "Mecklenburg-Vorpommern"),
        ("NI", "Niedersachsen"),
        ("NW", "Nordrhein-Westfalen"),
        ("RP", "Rheinland-Pfalz"),
        ("SL", "Saarland"),
        ("SN", "Sachsen (Freistaat)"),
        ("ST", "Sachsen-Anhalt"),
        ("SH", "Schleswig-Holstein"),
        ("TH", "Thüringen (Freistaat)"),
        ("OTHER", "Ausland"),
    )
    name = models.CharField(max_length=200, null=False)
    federal_state = models.CharField(
        choices=FEDERAL_STATE_CHOICES, max_length=100, blank=True, null=True
    )
    use_record_pool = models.BooleanField(default=False)
    # keys
    public_key = models.BinaryField(null=True)
    private_key = models.BinaryField(null=True)
    encrypted_fields = ["private_key"]
    encryption_class = AESEncryption

    class Meta:
        ordering = ["name"]
        verbose_name = "Rlc"
        verbose_name_plural = "Rlcs"

    @property
    def do_keys_exist(self):
        return self.public_key is not None or self.private_key is not None

    def __str__(self):
        return "rlc: {}; name: {};".format(self.pk, self.name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # create the root folder from files if it doesn't exist
        from apps.files.models import Folder

        if not Folder.objects.filter(rlc=self, parent=None).exists():
            Folder.objects.create(rlc=self, parent=None, name="Files")

    def decrypt(self, aes_key):
        super().decrypt(aes_key)

    def encrypt(self, aes_key):
        super().encrypt(aes_key)

    def get_public_key(self) -> bytes:
        # safety check
        if not self.do_keys_exist:
            self.generate_keys()
        # return the public key
        return self.encryption_keys.public_key

    def get_aes_key(self, user=None, private_key_user=None):
        # safety check
        if not self.do_keys_exist:
            self.generate_keys()

        if user and private_key_user:
            # get the aes key that encrypted the rlc private key. this aes key is encrypted for every user with its
            # public key, therefore only its private key can unlock the aes key.
            try:
                keys = user.users_rlc_keys.get(rlc=self)
            except ObjectDoesNotExist:
                keys = user.users_rlc_keys.create(rlc=self, user=user, correct=False, encrypted_key=b'')
            keys.decrypt(private_key_user)
            aes_key = keys.encrypted_key
            return aes_key

        else:
            raise ValueError("You need to pass (user and private_key_user).")

    def get_private_key(
        self, user: 'UserProfile' = None, private_key_user: str = None
    ) -> str:
        # safety check
        if not self.do_keys_exist:
            self.generate_keys()

        if user and private_key_user:

            try:
                keys = user.users_rlc_keys.get(rlc=self)
            except ObjectDoesNotExist:
                keys = user.users_rlc_keys.create(rlc=self, correct=False, encrypted_key=b'')
            keys.decrypt(private_key_user)
            aes_key = self.get_aes_key(user=user, private_key_user=private_key_user)

            self.decrypt(aes_key)

            return self.private_key

        else:
            raise ValueError("You need to pass (user and private_key_user).")

    def generate_keys(self) -> None:
        from .users_rlc_keys import UsersRlcKeys

        # safety return
        if self.do_keys_exist:
            return

        # generate some keys for rlc
        aes_key = AESEncryption.generate_secure_key()
        private_key, public_key = RSAEncryption.generate_keys()
        self.private_key = private_key
        self.public_key = public_key
        self.encrypt(aes_key)
        self.save()
        # create encryption keys for users to be able to decrypt rlc private key with users private key
        # the aes key is encrypted with the users public key, but only the user's private key can decrypt
        # the encrypted aes key
        for user in self.rlc_members.all():
            UsersRlcKeys.objects.filter(user=user, rlc=self).delete()
            user_rlc_keys = UsersRlcKeys(user=user, rlc=self, encrypted_key=aes_key)
            public_key_user = user.get_public_key()
            user_rlc_keys.encrypt(public_key_user)
            user_rlc_keys.save()

    def accept_member(self, admin: 'UserProfile', member: 'UserProfile', private_key_admin: str):
        from apps.core.models import UsersRlcKeys

        if not admin.has_permission(PERMISSION_ADMIN_MANAGE_USERS):
            return

        # create the rlc encryption keys for new member
        aes_key_rlc = self.get_aes_key(user=admin, private_key_user=private_key_admin)
        new_user_rlc_keys = UsersRlcKeys(user=member, rlc_id=self.id, encrypted_key=aes_key_rlc)
        public_key = member.get_public_key()
        new_user_rlc_keys.encrypt(public_key)

        # delete the old keys
        UsersRlcKeys.objects.filter(user=member).delete()

        # save the new keys
        new_user_rlc_keys.save()

        # set the user accepted field so that the user can login
        member.rlc_user.accepted = True
        member.rlc_user.save()

    def deactivate_member(self, admin: 'UserProfile', member: 'UserProfile'):
        pass

    def get_meta_information(self):
        return {
            "id": self.id,
            "name": self.name,
            "records": sum(
                [template.records.count() for template in self.recordtemplates.all()]
            ),
            "files": sum(
                [folder.files_in_folder.count() for folder in self.folders.all()]
            ),
            "collab": self.collab_documents.count(),
        }

    def force_delete(self):
        from apps.files.models.file import File
        from apps.recordmanagement.models.record import Record

        # delete records
        for r in Record.objects.filter(template__in=self.recordtemplates.all()):
            r.delete()
        # delete files
        for f in File.objects.filter(folder__in=self.folders.all()):
            f.delete()
        # delete collab
        for c in self.collab_documents.all():
            c.delete()
        # delete users
        for u in self.rlc_members.all():
            u.delete()
        # delete self
        self.delete()
