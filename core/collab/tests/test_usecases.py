from core.collab.models.collab import Collab
from core.collab.repositories.collab import CollabRepository
from core.collab.use_cases.collab import (
    create_collab,
    delete_collab,
    sync_collab,
    update_collab_title,
)
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.seedwork import test_helpers


def test_collab_creation(db):
    ou = test_helpers.create_org_user()
    user = ou["rlc_user"]
    f = test_helpers.create_folder(user=user)
    folder = f["folder"]
    collab = create_collab(
        __actor=user,
        title="Test Collab",
        folder_uuid=folder.uuid,
        cr=CollabRepository(),
        fr=DjangoFolderRepository(),
    )
    assert collab is not None
    assert collab.title == "Test Collab"
    assert Collab.objects.count() == 1


def test_collab_update(db):
    ou = test_helpers.create_org_user()
    user = ou["rlc_user"]
    f = test_helpers.create_folder(user=user)
    folder = f["folder"]
    collab = Collab.create(
        user=user,
        title="Test Collab",
        folder=folder,
    )
    cr = CollabRepository()
    cr.save_document(collab, user, folder)
    collab = update_collab_title(
        __actor=user,
        collab_uuid=collab.uuid,
        title="Updated Collab",
        cr=cr,
        fr=DjangoFolderRepository(),
    )
    assert Collab.objects.get(uuid=collab.uuid).title == "Updated Collab"


def test_collab_sync(db):
    ou = test_helpers.create_org_user()
    user = ou["rlc_user"]
    f = test_helpers.create_folder(user=user)
    folder = f["folder"]
    collab = Collab.create(
        user=user,
        title="Test Collab",
        folder=folder,
    )
    cr = CollabRepository()
    fr = DjangoFolderRepository()
    cr.save_document(collab, user, folder)
    sync_collab(user, collab.uuid, "my-awesome-text")
    loaded = cr.get_document(collab.uuid, user, fr)
    assert loaded.text == "my-awesome-text"


def test_collab_delete(db):
    ou = test_helpers.create_org_user()
    user = ou["rlc_user"]
    f = test_helpers.create_folder(user=user)
    folder = f["folder"]
    collab = Collab.create(
        user=user,
        title="Test Collab",
        folder=folder,
    )
    cr = CollabRepository()
    cr.save_document(collab, user, folder)
    delete_collab(user, collab.uuid)
    assert Collab.objects.count() == 0
