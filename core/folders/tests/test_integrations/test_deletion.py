import io
import sys

import pytest
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone

from core.auth.models import OrgUser, UserProfile
from core.collab.models.collab import Collab
from core.collab.repositories.collab import CollabRepository
from core.collab.use_cases.collab import create_collab
from core.data_sheets.models.data_sheet import DataSheet, DataSheetRepository
from core.data_sheets.models.template import DataSheetTemplate
from core.data_sheets.use_cases.sheet import create_a_data_sheet_within_a_folder
from core.files_new.models.file import EncryptedRecordDocument, FileRepository
from core.files_new.use_cases.file import upload_a_file
from core.folders.domain.aggregates.folder import Folder
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.permissions.static import PERMISSION_RECORDS_ADD_RECORD
from core.questionnaires.models.questionnaire import (
    Questionnaire,
    QuestionnaireRepository,
)
from core.questionnaires.models.template import QuestionnaireTemplate
from core.questionnaires.use_cases.questionnaire import publish_a_questionnaire
from core.rlc.models import Org
from core.timeline.models.event import TimelineEvent
from core.timeline.models.follow_up import TimelineFollowUp
from core.timeline.repositories.event import EventRepository
from core.timeline.repositories.follow_up import FollowUpRepository
from core.timeline.usecases.event import create_event
from core.timeline.usecases.follow_up import create_follow_up
from core.upload.models.upload import UploadLink, UploadLinkRepository
from core.upload.use_cases.upload import create_upload_link


@pytest.fixture
def user(db):
    o = Org.objects.create(name="Test")
    p = UserProfile.objects.create(email="dummy@law-orga.de", name="Mr. Dummy")
    u = OrgUser(user=p, org=o)
    u.generate_keys(settings.DUMMY_USER_PASSWORD)
    u.save()
    u.grant(PERMISSION_RECORDS_ADD_RECORD)
    o.generate_keys()
    user = OrgUser.objects.get(pk=u.pk)
    yield user


def test_all_items_inside_folder_are_deleted_when_folder_is_deleted(db, user):
    r = DjangoFolderRepository()
    f = Folder.create(name="New Folder", org_pk=user.org_id, stop_inherit=True)
    f.grant_access(to=user)
    r.save(f)

    collab = create_collab(user, "TestCollab", f.uuid)
    assert Collab.objects.filter(pk=collab.pk).exists()

    template = DataSheetTemplate.objects.create(name="TestTemplate", rlc_id=user.org_id)
    sheet = create_a_data_sheet_within_a_folder(user, "TestRecord", f.uuid, template.pk)
    assert DataSheet.objects.filter(pk=sheet.pk).exists()

    qtemplate = QuestionnaireTemplate.objects.create(
        name="TestTemplate", rlc_id=user.org_id
    )
    questionnaire = publish_a_questionnaire(user, f.uuid, qtemplate.pk)
    assert Questionnaire.objects.filter(pk=questionnaire.pk).exists()

    event = create_event(user, "TestEvent", "Text", timezone.now(), f.uuid)
    assert TimelineEvent.objects.filter(pk=event.pk).exists()

    follow_up = create_follow_up(user, "TestFollowUp", "Text", timezone.now(), f.uuid)
    assert TimelineFollowUp.objects.filter(pk=follow_up.pk).exists()

    file_content = io.BytesIO(bytes("What an awesome file :)", "utf-8"))
    raw_file = InMemoryUploadedFile(
        file=file_content,
        field_name=None,
        name="Test",
        content_type="TXT",
        size=sys.getsizeof(file_content),
        charset="utf-8",
    )
    file = upload_a_file(user, raw_file, f.uuid)
    assert EncryptedRecordDocument.objects.filter(pk=file.pk).exists()

    link = create_upload_link(user, "TestLink", f.uuid)
    assert UploadLink.objects.filter(pk=link.pk).exists()

    r.delete(
        f,
        [
            CollabRepository(),
            DataSheetRepository(),
            QuestionnaireRepository(),
            EventRepository(),
            FollowUpRepository(),
            FileRepository(),
            UploadLinkRepository(),
        ],
    )

    assert Collab.objects.filter(pk=collab.pk).exists() is False
    assert DataSheet.objects.filter(pk=sheet.pk).exists() is False
    assert Questionnaire.objects.filter(pk=questionnaire.pk).exists() is False
    assert TimelineEvent.objects.filter(pk=event.pk).exists() is False
    assert TimelineFollowUp.objects.filter(pk=follow_up.pk).exists() is False
    assert EncryptedRecordDocument.objects.filter(pk=file.pk).exists() is False
    assert UploadLink.objects.filter(pk=link.pk).exists() is False
