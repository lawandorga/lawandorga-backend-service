from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from django.db import models
from django.utils import timezone

from core.auth.models import RlcUser
from core.data_sheets.models import Record
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.item import ItemRepository
from core.folders.domain.value_objects.asymmetric_key import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
)
from core.folders.infrastructure.folder_addon import FolderAddon
from core.questionnaires.models.template import (
    QuestionnaireQuestion,
    QuestionnaireTemplate,
)
from core.seedwork.aggregate import Aggregate
from core.seedwork.encryption import AESEncryption, EncryptedModelMixin, RSAEncryption
from core.seedwork.events_addon import EventsAddon
from core.seedwork.storage import download_and_decrypt_file, encrypt_and_upload_file


class DjangoQuestionnaireRepository(ItemRepository):
    IDENTIFIER = "QUESTIONNAIRE"

    @classmethod
    def retrieve(cls, uuid: UUID, org_pk: Optional[int] = None) -> "Questionnaire":
        return Questionnaire.objects.get(uuid=uuid, template__rlc_id=org_pk)


class Questionnaire(Aggregate, models.Model):
    REPOSITORY = DjangoQuestionnaireRepository.IDENTIFIER

    @classmethod
    def create(
        cls, template: QuestionnaireTemplate, folder: Folder, user: RlcUser
    ) -> "Questionnaire":
        name = f"{template.name}: {timezone.now().strftime('%d.%m.%Y')}"
        questionnaire = Questionnaire(template=template, name=name)
        questionnaire.folder.put_obj_in_folder(folder)
        questionnaire.generate_key(user)
        questionnaire.generate_code()
        return questionnaire

    record: Optional[Record] = models.ForeignKey(  # type: ignore
        Record,
        on_delete=models.CASCADE,
        related_name="questionnaires",
        null=True,
        blank=True,
    )
    template = models.ForeignKey(
        QuestionnaireTemplate, on_delete=models.PROTECT, related_name="questionnaires"
    )
    code = models.SlugField(unique=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, default="-")
    uuid = models.UUIDField(default=uuid4, unique=True)
    folder_uuid = models.UUIDField(null=True)
    key = models.JSONField(null=True)

    addons = dict(events=EventsAddon, folder=FolderAddon)
    events: EventsAddon
    folder: FolderAddon

    if TYPE_CHECKING:
        answers: models.QuerySet["QuestionnaireAnswer"]

    class Meta:
        verbose_name = "RecordQuestionnaire"
        verbose_name_plural = "RecordQuestionnaires"

    def __str__(self):
        return "recordQuestionnaire: {};".format(self.pk)

    @property
    def org_pk(self) -> int:
        return self.template.rlc_id

    @property
    def answered(self):
        return self.answers.all().count() - self.template.fields.all().count() == 0

    def generate_code(self):
        assert self.code is None or self.code == ""
        self.code = str(uuid4())[:6].upper()

    def get_public_key(self):
        assert self.key is None
        return self.template.rlc.get_public_key()

    def get_private_key(self, private_key_user=None, user: RlcUser | None = None):
        assert self.key is None
        assert user is not None
        return self.template.rlc.get_private_key(
            user=user.user, private_key_user=private_key_user
        )

    def generate_key(self, user: RlcUser):
        assert self.folder is not None

        key = AsymmetricKey.generate()
        lock_key = self.folder.get_encryption_key(requestor=user)
        enc_key = EncryptedAsymmetricKey.create(key, lock_key)
        self.key = enc_key.as_dict()

    def get_key(
        self, user: Optional[RlcUser] = None
    ) -> AsymmetricKey | EncryptedAsymmetricKey:
        assert self.folder is not None
        assert self.key is not None

        enc_key = EncryptedAsymmetricKey.create_from_dict(self.key)
        if user is None:
            return enc_key

        unlock_key = self.folder.get_decryption_key(requestor=user)
        key = enc_key.decrypt(unlock_key)
        return key

    def put_in_folder(self, user: RlcUser):
        assert self.folder_uuid is None
        if self.record and self.record.folder and self.record.folder.has_access(user):
            # set folder
            folder = self.record.folder.folder
            self.folder.put_obj_in_folder(folder)

            # copy key
            public_key = self.get_public_key().decode("utf-8")
            private_key = self.get_private_key(user.get_private_key(), user)
            origin = "A1"
            key = AsymmetricKey.create(
                public_key=public_key, private_key=private_key, origin=origin
            )
            lock_key = folder.get_encryption_key(requestor=user)
            enc_key = EncryptedAsymmetricKey.create(key, lock_key)
            self.key = enc_key.as_dict()

            # save
            self.save()

    def add_answer(
        self, question: QuestionnaireQuestion, answer: str
    ) -> "QuestionnaireAnswer":
        a = QuestionnaireAnswer(questionnaire=self, field=question, data=answer)
        a.encrypt()
        return a


class QuestionnaireAnswer(EncryptedModelMixin, models.Model):
    questionnaire = models.ForeignKey(
        Questionnaire, on_delete=models.CASCADE, related_name="answers"
    )
    field = models.ForeignKey(
        QuestionnaireQuestion, on_delete=models.CASCADE, related_name="answers"
    )
    data = models.BinaryField()
    aes_key = models.BinaryField(default=b"")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    encrypted_fields = ["data", "aes_key"]
    encryption_class = RSAEncryption

    # midterm: remove EncryptedModelMixin
    # enc_key = models.JSONField()
    # enc_data = models.JSONField()

    class Meta:
        verbose_name = "QuestionnaireAnswer"
        verbose_name_plural = "QuestionnaireAnswers"

    def __str__(self):
        return "questionnaireAnswer: {};".format(self.pk)

    @property
    def filename(self) -> str:
        if not self.field.type == "FILE":
            raise ValueError("This field is not a file.")
        assert isinstance(self.data, str)
        return self.data.split("/")[-1]

    def encrypt(self, *args):
        key = self.questionnaire.get_key().get_public_key().encode("utf-8")
        super().encrypt(key)

    def decrypt(self, user=None):
        key = self.questionnaire.get_key(user=user).get_private_key().decode("utf-8")
        super().decrypt(key)
        return self

    def generate_key(self):
        key = "core/questionnaires/{}/{}".format(
            self.questionnaire.folder_uuid, uuid4()
        )
        return key

    def download_file(self, aes_key):
        file_key = "{}.enc".format(self.data)
        return download_and_decrypt_file(file_key, aes_key)

    def upload_file(self, file):
        self.aes_key = AESEncryption.generate_secure_key()
        self.data = "{}/{}".format(self.generate_key(), file.name)
        key = "{}.enc".format(self.data)
        encrypt_and_upload_file(file, key, self.aes_key)
