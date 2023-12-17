from django.test import Client

from core.folders.domain.aggregates.folder import Folder
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.seedwork import test_helpers


def test_folder_can_be_retrieved(db):
    user = test_helpers.create_org_user()
    rlc_uesr = user["rlc_user"]
    repository = DjangoFolderRepository()
    folder1 = Folder.create(name="New Folder", org_pk=rlc_uesr.org_id)
    folder1.grant_access(to=rlc_uesr)
    repository.save(folder1)
    client = Client()
    client.login(**user)
    response = client.get(f"/api/folders/query/{folder1.uuid}/")
    assert response.status_code == 200, response.json()
