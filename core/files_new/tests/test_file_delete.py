from core.files_new.models import EncryptedRecordDocument
from core.files_new.use_cases.file import delete_file
from core.folders.domain.aggregates.folder import Folder
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from messagebus.domain.collector import EventCollector


def test_delete_removes_it_from_folder(db, user, file):
    user.user.save()
    user.org.save()
    user.save()
    folder = Folder.create(name="Test Folder", org_pk=user.org.pk)
    folder.grant_access(user)
    r = DjangoFolderRepository()
    r.save(folder)
    file = EncryptedRecordDocument.create(
        file=file, folder=folder, by=user, collector=EventCollector()
    )
    file.save()
    delete_file(user, file.uuid)
    folder = r.retrieve(user.org.pk, folder.uuid)
    assert len(folder.items) == 0
