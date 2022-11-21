import uuid
from typing import Optional
from uuid import UUID

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.aggregates.upgrade import Item, Upgrade
from core.folders.domain.repositiories.upgrade import UpgradeRepository
from core.folders.domain.types import StrDict
from core.folders.domain.value_objects.keys import SymmetricKey
from core.records.models import Record


class RecordUpgradeRepository(UpgradeRepository):
    IDENTIFIER = "RECORD_UPGRADE"

    @classmethod
    def create_from_dict(
        cls, d: Optional[StrDict] = None, folder: Optional[Folder] = None
    ) -> "RecordUpgrade":
        assert (
            d is not None
            and folder is not None
            and "pk" in d
            and isinstance(d["pk"], str)
            and "repository" in d
            and isinstance(d["repository"], str)
            # and 'token' in d
            # and isinstance(d['token'], str)
        )

        assert d["repository"] == cls.IDENTIFIER

        pk = UUID(d["pk"])

        return RecordUpgrade(pk=pk, folder=folder)
        # return RecordUpgrade(token=d['token'], pk=d['pk'], folder=folder)


class RecordUpgrade(Upgrade):
    REPOSITORY = RecordUpgradeRepository.IDENTIFIER

    @classmethod
    def create(cls, folder: Optional["Folder"] = None) -> "RecordUpgrade":
        return RecordUpgrade(folder=folder, pk=uuid.uuid4())

    def __init__(self, folder: Optional["Folder"] = None, pk: Optional[UUID] = None):
        # assert token is not None
        # self.__token = token
        super().__init__(folder=folder, pk=pk)

    def __str__(self):
        return "recordUpgrade: {}; token: {};".format(self.pk, self.token)

    def __dict__(self) -> StrDict:  # type: ignore
        d = super().__dict__()
        return d
        # return {**d, 'token': self.__token}

    # @property
    # def token(self):
    #     return self.__token

    @property
    def content(self) -> list[Item]:
        records_1 = list(Record.objects.filter(upgrade_pk=self.pk))
        records_2 = map(lambda x: Item(x.identifier), records_1)
        records_3 = list(records_2)
        return records_3

    def reencrypt(self, old_key: SymmetricKey, new_key: SymmetricKey):
        pass
