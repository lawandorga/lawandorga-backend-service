import json
from typing import Optional, Union, cast
from uuid import UUID, uuid4

from django.core.files import File as DjangoFile
from django.db import models, transaction
from django.utils.timezone import localtime

from core.auth.models import RlcUser
from core.folders.domain.aggregates.folder import Folder, Item
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.repositiories.item import ItemRepository
from core.folders.domain.value_objects.box import OpenBox
from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1
from core.records.models import EncryptedClient  # type: ignore
from core.records.models.template import (
    RecordEncryptedFileField,
    RecordEncryptedSelectField,
    RecordEncryptedStandardField,
    RecordMultipleField,
    RecordSelectField,
    RecordStandardField,
    RecordStateField,
    RecordStatisticField,
    RecordTemplate,
    RecordUsersField,
)
from core.seedwork.encryption import AESEncryption, EncryptedModelMixin, RSAEncryption

###
# Record
###
from core.seedwork.repository import RepositoryWarehouse


class DjangoRecordRepository(ItemRepository):
    IDENTIFIER = "RECORD"

    @classmethod
    def retrieve(cls, uuid: UUID) -> "Record":
        return Record.objects.get(uuid=uuid)


class Record(Item, models.Model):
    REPOSITORY = "RECORD"

    template = models.ForeignKey(
        RecordTemplate, related_name="records", on_delete=models.PROTECT
    )
    folder_uuid = models.UUIDField(db_index=True, null=True)
    uuid = models.UUIDField(default=uuid4, unique=True, db_index=True)
    old_client = models.ForeignKey(
        EncryptedClient,
        related_name="records",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    key = models.JSONField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Record"
        verbose_name_plural = "Records"

    def __str__(self):
        return "record: {}; rlc: {};".format(self.pk, self.template.rlc.name)

    @property
    def actions(self):
        return {"OPEN": "/records/{}/".format(self.pk)}

    @property
    def name(self):
        return self.identifier

    @property
    def identifier(self):
        first_standard_entry = self.standard_entries.order_by("field__order").first()
        if first_standard_entry:
            return first_standard_entry.value
        return None

    @property
    def delete_requested(self) -> bool:
        deletions = getattr(self, "deletions").all()
        for deletion in deletions:
            if deletion.state == "re":
                return True
        return False

    @property
    def attributes(self) -> dict[str, Union[list[str], str]]:
        entries: dict[str, Union[list[str], str]] = {
            "Created": localtime(self.created).strftime("%d.%m.%y %H:%M"),
            "Updated": localtime(self.updated).strftime("%d.%m.%y %H:%M"),
        }
        for entry_type in self.get_unencrypted_entry_types():
            for entry in getattr(self, entry_type).all():
                entries[entry.field.name] = entry.get_value()
        return entries

    @staticmethod
    def get_unencrypted_prefetch_related():
        return [
            "state_entries",
            "state_entries__field",
            "select_entries",
            "select_entries__field",
            "standard_entries",
            "standard_entries__field",
            "users_entries",
            "users_entries__value",
            "users_entries__field",
            "multiple_entries",
            "multiple_entries__field",
            "encryptions",
            "deletions",
        ]

    def grant_access(self, to: RlcUser, by: Optional[RlcUser]):
        if self.folder is not None:
            r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
            folder = self.folder
            if not folder.has_access(to):
                folder.grant_access(to=to, by=by)
                r.save(folder)
        else:
            raise ValueError("This record has no upgrade.")

    def has_access(self, user: RlcUser) -> bool:
        if self.folder is None:
            for enc in getattr(self, "encryptions").all():
                if enc.user_id == user.id:
                    return True
        else:
            return self.folder.has_access(user)
        return False

    def generate_key(self, user: RlcUser):
        assert self.folder is not None
        key = SymmetricKey.generate()
        lock_key = self.folder.get_encryption_key(requestor=user)
        enc_key = EncryptedSymmetricKey.create(key, lock_key)
        self.key = enc_key.as_dict()

    def set_folder(self, folder: "Folder"):
        super().set_folder(folder)
        self._folder = folder

    @property
    def folder(self) -> Optional[Folder]:
        if self.folder_uuid is None:
            return None
        if not hasattr(self, "_folder"):
            folders = self.__get_folders()
            # get folder from the set cache
            if folders is not None:
                self._folder = folders[self.folder_uuid]
            # get folder from the repository (many queries)
            else:
                r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
                self._folder = r.retrieve(self.template.rlc_id, self.folder_uuid)
        return self._folder

    def get_aes_key(self, user: RlcUser, *args, **kwargs):
        if self.folder is None:
            self.put_in_folder(user)

        assert self.folder is not None

        if self.key is None:
            aes_key = self.get_aes_key_old(user)
            aes_key_box = OpenBox(data=bytes(aes_key, "utf-8"))
            key = SymmetricKey(key=aes_key_box, origin=SymmetricEncryptionV1.VERSION)
            folder = self.folder
            encryption_key = folder.get_encryption_key(requestor=user)
            self.key = EncryptedSymmetricKey.create(key, encryption_key).as_dict()

            r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
            with transaction.atomic():
                r.save(folder)
                self.save()

        decryption_key = self.folder.get_decryption_key(requestor=user)
        enc_key = EncryptedSymmetricKey.create_from_dict(self.key)
        key = enc_key.decrypt(decryption_key)
        return key.get_key()

    @classmethod
    def __get_folders_attribute_key(cls, org_pk: int):
        name = 'folders---{}'.format(org_pk)
        return name

    def __get_folders(self) -> Optional[dict[UUID, Folder]]:
        return getattr(self, self.__get_folders_attribute_key(self.template.rlc_id), None)

    @classmethod
    def set_folders(cls, org_pk: int):
        name = cls.__get_folders_attribute_key(org_pk)
        r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
        folders = r.dict(org_pk)
        setattr(cls, name, folders)

    def get_aes_key_old(self, user: RlcUser):
        private_key_user = user.get_decryption_key().get_private_key()
        encryption = self.encryptions.get(user=user)
        encryption.decrypt(private_key_user)
        key = encryption.key
        return key

    def get_unencrypted_entry_types(self):
        return ["state_entries", "standard_entries", "select_entries", "users_entries"]

    def get_encrypted_entry_types(self):
        return [
            "encrypted_select_entries",
            "encrypted_file_entries",
            "encrypted_standard_entries",
        ]

    def get_all_entry_types(self):
        return self.get_unencrypted_entry_types() + self.get_encrypted_entry_types()

    def get_entries(
        self, entry_types_and_serializers, aes_key_record=None, request=None, sort=False
    ):
        # this might look weird, but i've done it this way to optimize performance
        # with prefetch related
        # and watch out this expects a self from a query which has prefetched
        # all the relevant unencrypted entries otherwise the queries explode
        entries = {}
        for (entry_type, serializer) in entry_types_and_serializers:
            for entry in getattr(self, entry_type).all():
                if entry.encrypted_entry:
                    entry.decrypt(aes_key_record=aes_key_record)
                entries[entry.field.name] = serializer(
                    instance=entry, context={"request": request}
                ).data
        if sort:
            entries = dict(sorted(entries.items(), key=lambda item: item[1]["order"]))
        return entries

    def put_in_folder(self, user: RlcUser):
        if not self.has_access(user):
            raise ValueError("User has no access to this folder.")
        r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))

        records_folder = r.get_or_create_records_folder(
            org_pk=self.template.rlc_id, user=user
        )

        folder_name = "{}".format(self.identifier or "Not-Set")
        folder = Folder.create(
            folder_name, org_pk=self.template.rlc_id, stop_inherit=True
        )
        folder.grant_access(user)
        folder.set_parent(records_folder, user)
        for encryption in list(self.encryptions.exclude(user_id=user.id)):
            folder.grant_access(to=encryption.user, by=user)

        folder.add_item(self)

        with transaction.atomic():
            r.save(folder)
            self.save()


###
# RecordEntry
###
class RecordEntry(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # used in record for get_entries
    encrypted_entry = False

    class Meta:
        abstract = True

    def get_value(self, *args, **kwargs):
        raise NotImplementedError("This method needs to be implemented")


class RecordEntryEncryptedModelMixin(EncryptedModelMixin):
    encryption_class = AESEncryption

    # used in record for get entries
    encrypted_entry = True

    def encrypt(
        self, user: Optional[RlcUser] = None, private_key_user=None, aes_key_record=None
    ):
        record: Record = self.record  # type: ignore
        if user and private_key_user:
            key = record.get_aes_key(user=user, private_key_user=private_key_user)
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError(
                "You have to set (aes_key_record) or (user and private_key_user)."
            )
        super().encrypt(key)

    def decrypt(
        self, user: Optional[RlcUser] = None, private_key_user=None, aes_key_record=None
    ):
        record: Record = self.record  # type: ignore
        if user and private_key_user:
            key = record.get_aes_key(user=user, private_key_user=private_key_user)
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError(
                "You have to set (aes_key_record) or (user and private_key_user)."
            )
        super().decrypt(key)


class RecordStateEntry(RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="state_entries"
    )
    field = models.ForeignKey(
        RecordStateField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.CharField(max_length=1000)
    closed_at = models.DateTimeField(blank=True, null=True, default=None)

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordStateEntry"
        verbose_name_plural = "RecordStateEntries"

    def __str__(self):
        return "recordStateEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.value


class RecordUsersEntry(RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="users_entries"
    )
    field = models.ForeignKey(
        RecordUsersField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.ManyToManyField(RlcUser, blank=True)

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordUsersEntry"
        verbose_name_plural = "RecordUsersEntries"

    def __str__(self):
        return "recordUsersEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        # this might look weird, but i've done it this way to optimize performance
        # with prefetch related
        users = []
        for user in getattr(self, "value").all():
            users.append(user.name)
        return users


class RecordSelectEntry(RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="select_entries"
    )
    field = models.ForeignKey(
        RecordSelectField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.CharField(max_length=200)

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordSelectEntry"
        verbose_name_plural = "RecordSelectEntries"

    def __str__(self):
        return "recordSelectEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.value


class RecordMultipleEntry(RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="multiple_entries"
    )
    field = models.ForeignKey(
        RecordMultipleField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.JSONField()

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordMultipleEntry"
        verbose_name_plural = "RecordMultipleEntries"

    def __str__(self):
        return "recordMultipleEntry: {}".format(self.pk)


class RecordEncryptedSelectEntry(RecordEntryEncryptedModelMixin, RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="encrypted_select_entries"
    )
    field = models.ForeignKey(
        RecordEncryptedSelectField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.BinaryField()

    # encryption
    encrypted_fields = ["value"]

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordEncryptedSelectEntry"
        verbose_name_plural = "RecordEncryptedSelectEntries"

    def __str__(self):
        return "recordEncryptedSelectEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        if self.encryption_status == "ENCRYPTED":
            self.decrypt(*args, **kwargs)
        return self.value

    def encrypt(self, *args, **kwargs):
        self.value = json.dumps(self.value)
        super().encrypt(*args, **kwargs)

    def decrypt(self, *args, **kwargs):
        super().decrypt(*args, **kwargs)
        self.value = json.loads(self.value)


class RecordEncryptedFileEntry(RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="encrypted_file_entries"
    )
    field = models.ForeignKey(
        RecordEncryptedFileField, related_name="entries", on_delete=models.PROTECT
    )
    file = models.FileField(upload_to="recordmanagement/recordencryptedfileentry/")

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordEncryptedFileEntry"
        verbose_name_plural = "RecordEncryptedFileEntries"

    def __str__(self):
        return "recordEncryptedFileEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.file.name.split("/")[-1].replace(".enc", "")

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    @staticmethod
    def encrypt_file(
        file, record, user=None, private_key_user=None, aes_key_record=None
    ):
        if user and private_key_user:
            key = record.get_aes_key(
                user=user.rlc_user, private_key_user=private_key_user
            )
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError(
                "You have to set (aes_key_record) or (user and private_key_user)."
            )
        name = file.name
        file = AESEncryption.encrypt_in_memory_file(file, key)
        file = DjangoFile(file, name="{}.enc".format(name))
        return file

    def decrypt_file(
        self, user: Optional[RlcUser] = None, private_key_user=None, aes_key_record=None
    ):
        if user and private_key_user:
            key = self.record.get_aes_key(user=user, private_key_user=private_key_user)
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError(
                "You have to set (aes_key_record) or (user and private_key_user)."
            )
        file = AESEncryption.decrypt_bytes_file(self.file, key)
        file.seek(0)
        return file


class RecordStandardEntry(RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="standard_entries"
    )
    field = models.ForeignKey(
        RecordStandardField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.TextField(max_length=20000)

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordStandardEntry"
        verbose_name_plural = "RecordStandardEntries"

    def __str__(self):
        return "recordStandardEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.value


class RecordEncryptedStandardEntry(RecordEntryEncryptedModelMixin, RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="encrypted_standard_entries"
    )
    field = models.ForeignKey(
        RecordEncryptedStandardField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.BinaryField()

    # encryption
    encryption_class = AESEncryption
    encrypted_fields = ["value"]

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordStandardEntry"
        verbose_name_plural = "RecordStandardEntries"

    def __str__(self):
        return "recordEncryptedStandardEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        if self.encryption_status == "ENCRYPTED" or self.encryption_status is None:
            self.decrypt(*args, **kwargs)
        return self.value


class RecordStatisticEntry(RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="statistic_entries"
    )
    field = models.ForeignKey(
        RecordStatisticField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.CharField(max_length=200)

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordStatisticEntry"
        verbose_name_plural = "RecordStatisticEntries"

    def __str__(self):
        return "recordStatisticEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.value


###
# RecordEncryption
###
class RecordEncryptionNew(EncryptedModelMixin, models.Model):
    user = models.ForeignKey(
        RlcUser, related_name="recordencryptions", on_delete=models.CASCADE
    )
    record = models.ForeignKey(
        Record, related_name="encryptions", on_delete=models.CASCADE
    )
    key = models.BinaryField()
    correct = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    encryption_class = RSAEncryption
    encrypted_fields = ["key"]

    class Meta:
        unique_together = ["user", "record"]
        verbose_name = "RecordEncryption"
        verbose_name_plural = "RecordEncryptions"

    def __str__(self):
        return "recordEncryption: {}; user: {}; record: {};".format(
            self.pk, self.user.email, self.record.pk
        )

    def set_correct(self, value):
        key = RecordEncryptionNew.objects.get(pk=self.pk)
        key.correct = value
        key.save()
        self.correct = value

    def test(self, private_key_user):
        try:
            super().decrypt(private_key_user)
            self.set_correct(True)
        except ValueError:
            self.set_correct(False)
            self.user.locked = True
            self.user.save()

    def decrypt(self, private_key_user=None):
        if private_key_user:
            key = private_key_user
        else:
            raise ValueError("You need to pass (private_key_user).")
        try:
            super().decrypt(key)
        except Exception as e:
            self.test(private_key_user)
            raise e

    def encrypt(self, public_key_user=None):
        if public_key_user:
            key = public_key_user
        else:
            raise ValueError("You need to pass (public_key_user).")
        super().encrypt(key)
