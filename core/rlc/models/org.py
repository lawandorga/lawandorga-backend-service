import uuid
from typing import TYPE_CHECKING, Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction

from core.seedwork.encryption import AESEncryption, EncryptedModelMixin, RSAEncryption

from .meta import Meta

if TYPE_CHECKING:
    from core.auth.models import OrgUser, UserProfile
    from core.collab.models import CollabDocument
    from core.collab.models.collab import Collab
    from core.collab.models.footer import Footer
    from core.collab.models.letterhead import Letterhead
    from core.collab.models.template import Template
    from core.data_sheets.models.template import DataSheetTemplate
    from core.events.models import EventsEvent
    from core.files.models.folder import Folder
    from core.folders.models import FOL_Folder
    from core.questionnaires.models.template import QuestionnaireTemplate
    from core.records.models.record import RecordsRecord
    from core.rlc.models.group import Group


class Org(EncryptedModelMixin, models.Model):
    @classmethod
    def create(cls, name: str, pk=0) -> "Org":
        org = Org(name=name)
        if pk:
            org.pk = pk
        return org

    meta = models.ForeignKey(Meta, on_delete=models.CASCADE, null=True, blank=True)
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
    collab_migrated = models.BooleanField(default=False)
    new_records_have_inheritance_stop = models.BooleanField(default=True)

    # keys
    public_key = models.BinaryField(null=True)
    private_key = models.BinaryField(null=True)
    encrypted_fields = ["private_key"]
    encryption_class = AESEncryption

    if TYPE_CHECKING:
        collab_documents: models.QuerySet["CollabDocument"]
        collabs: models.QuerySet["Collab"]
        folders_folders: models.QuerySet["FOL_Folder"]
        users: models.QuerySet[OrgUser]
        group_from_rlc: models.QuerySet[Group]
        events: models.QuerySet[EventsEvent]
        external_links: models.QuerySet["ExternalLink"]
        recordtemplates: models.QuerySet["DataSheetTemplate"]
        folders: models.QuerySet["Folder"]
        records_records: models.QuerySet["RecordsRecord"]
        questionnaire_templates: models.QuerySet["QuestionnaireTemplate"]
        letterheads: models.QuerySet["Letterhead"]
        footers: models.QuerySet["Footer"]
        templates: models.QuerySet["Template"]

    class Meta:
        ordering = ["name"]
        verbose_name = "ORG_Org"
        verbose_name_plural = "ORG_Orgs"

    @property
    def do_keys_exist(self):
        return self.public_key is not None or self.private_key is not None

    @property
    def links(self):
        return list(self.external_links.all())

    def __str__(self):
        return "rlc: {}; name: {};".format(self.pk, self.name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # create the root folder from files if it doesn't exist
        from core.models import Folder

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
        if self.public_key is not None:
            return bytes(self.public_key)
        raise ValueError("The public key can not be None.")

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
                keys = user.users_rlc_keys.create(
                    rlc=self, user=user, correct=False, encrypted_key=b""
                )
            keys.decrypt(private_key_user)
            aes_key = keys.encrypted_key
            return aes_key

        else:
            raise ValueError("You need to pass (user and private_key_user).")

    def get_private_key(
        self,
        user: Optional["UserProfile"] = None,
        private_key_user: Optional[str] = None,
    ) -> str:
        # safety check
        if not self.do_keys_exist:
            self.generate_keys()

        if user and private_key_user:
            try:
                keys = user.users_rlc_keys.get(rlc=self)
            except ObjectDoesNotExist:
                keys = user.users_rlc_keys.create(
                    rlc=self, correct=False, encrypted_key=b""
                )
            keys.decrypt(private_key_user)
            aes_key = self.get_aes_key(user=user, private_key_user=private_key_user)

            self.decrypt(aes_key)

            private_key: str = self.private_key  # type: ignore

            return private_key  # type: ignore

        else:
            raise ValueError("You need to pass (user and private_key_user).")

    def reset_keys(self):
        self.private_key = None
        self.public_key = None
        self.generate_keys()

    def generate_keys(self) -> None:
        from .org_encryption import OrgEncryption

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
        for rlc_user in self.users.all():
            OrgEncryption.objects.filter(user=rlc_user.user, rlc=self).delete()
            user_rlc_keys = OrgEncryption(
                user=rlc_user.user, rlc=self, encrypted_key=aes_key
            )
            public_key_user = rlc_user.user.get_public_key()
            user_rlc_keys.encrypt(public_key_user)
            user_rlc_keys.save()

    def accept_member(self, admin: "OrgUser", member: "OrgUser"):
        from core.folders.infrastructure.folder_repository import DjangoFolderRepository
        from core.models import OrgEncryption

        # create the rlc encryption keys for new member
        private_key_admin = admin.get_private_key()
        aes_key_rlc = self.get_aes_key(
            user=admin.user, private_key_user=private_key_admin
        )
        org_enc = OrgEncryption(
            user=member.user, rlc_id=self.pk, encrypted_key=aes_key_rlc
        )
        public_key = member.get_public_key()
        org_enc.encrypt(public_key)

        # grant access to the records folder
        r = DjangoFolderRepository()
        folder = r.get_or_create_records_folder(admin.org_id, admin)
        if not folder.has_access(member):
            folder.grant_access(member, admin)

        with transaction.atomic():
            # save the folder
            r.save(folder)

            # delete the old keys
            OrgEncryption.objects.filter(user=member.user).delete()

            # save the new keys
            org_enc.save()

            # set the user accepted field so that the user can login
            member.accepted = True
            member.save()

    def deactivate_member(self, admin: "UserProfile", member: "UserProfile"):
        pass

    def get_meta_information(self):
        return {
            "id": self.pk,
            "name": self.name,
            "records": sum(
                [template.records.count() for template in self.recordtemplates.all()]
            ),
            "files": sum(
                [folder.files_in_folder.count() for folder in self.folders.all()]
            ),
            "collab": self.collab_documents.count(),
        }

    def force_empty(self):
        from core.data_sheets.models import DataSheet
        from core.files.models import File

        for r in DataSheet.objects.filter(template__in=self.recordtemplates.all()):
            r.delete()
        for f in File.objects.filter(folder__in=self.folders.all()):
            f.delete()
        for fo in self.folders.all():
            fo.delete()
        for c in self.collab_documents.all():
            c.delete()
        for cnew in self.collabs.all():
            cnew.delete()
        for folder in self.folders_folders.all():
            folder.delete()
        for group in self.group_from_rlc.all():
            group.delete()
        for record in self.records_records.all():
            record.delete()
        for template in self.questionnaire_templates.all():
            template.questionnaires.all().delete()
            template.delete()
        self.reset_keys()
        self.save()

    def force_delete(self):
        from core.auth.models import UserProfile

        self.force_empty()
        # delete users
        user_ids = []
        for u in self.users.all():
            user_ids.append(u.user_id)
            u.delete()
        for u in list(UserProfile.objects.filter(id__in=user_ids)):
            u.delete()
        # delete self
        self.delete()


class ExternalLink(models.Model):
    org = models.ForeignKey(
        Org, related_name="external_links", on_delete=models.CASCADE
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    link = models.URLField(max_length=1000)
    order = models.IntegerField()

    class Meta:
        ordering = ["order"]
        verbose_name = "ExternalLink"
        verbose_name_plural = "ExternalLinks"

    def __str__(self):
        return "externalLink: {}; name: {};".format(self.id, self.name)
