from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.folders.models import FOL_ClosureTable, FOL_Folder
from core.folders.use_cases.folder import (
    create_folder,
    delete_folder,
    move_folder,
    rename_folder,
)
from core.tests import test_helpers


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


def test_move_folder_updates_child_closures(db):
    repo = DjangoFolderRepository()
    org_user = test_helpers.create_raw_org_user(save=True)
    folder = test_helpers.create_raw_folder(
        user=org_user, name="A", repo=repo, save=True
    )
    to_move = test_helpers.create_raw_folder(user=org_user, name="B")
    to_move.set_parent(folder, org_user)
    repo.save(to_move)
    subfolder = test_helpers.create_raw_folder(user=org_user, name="C")
    subfolder.set_parent(to_move, org_user)
    repo.save(subfolder)
    assert (
        FOL_ClosureTable.objects.filter(
            child__uuid=subfolder.uuid, parent__uuid__in=[to_move.uuid, folder.uuid]
        ).count()
        == 2
    )

    new_root = test_helpers.create_raw_folder(
        user=org_user, name="D", repo=repo, save=True
    )
    move_folder(org_user, to_move.uuid, new_root.uuid)
    assert FOL_ClosureTable.objects.filter(parent__uuid=to_move.uuid).count() == 1
    assert (
        FOL_ClosureTable.objects.filter(
            child__uuid=subfolder.uuid, parent__uuid__in=[to_move.uuid, new_root.uuid]
        ).count()
        == 2
    )
