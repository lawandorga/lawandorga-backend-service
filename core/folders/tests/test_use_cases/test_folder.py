
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.folders.models import FOL_Folder
from core.folders.use_cases.folder import create_folder, delete_folder, rename_folder
from core.seedwork import test_helpers



def test_create_folder(db):
    org_user = test_helpers.create_org_user()["org_user"]
    create_folder(org_user, "Test Folder", None)
    assert org_user.org.folders_folders.count() == 1


def test_rename_folder(db):
    org_user = test_helpers.create_org_user()["org_user"]
    folder = test_helpers.create_folder("Test Folder", org_user)["folder"]
    rename_folder(org_user, "New Folder", folder.uuid)
    folder = DjangoFolderRepository().retrieve(org_user.org_id, folder.uuid)
    assert folder.name == "New Folder"


def test_delete_folder(db):
    org_user = test_helpers.create_org_user()["org_user"]
    folder = test_helpers.create_folder("Test Folder", org_user)["folder"]
    delete_folder(org_user, folder.uuid)
    assert FOL_Folder.objects.get(uuid=folder.uuid).deleted
