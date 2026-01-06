from django.utils import timezone

from core.auth.models.org_user import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.tests import test_helpers
from core.timeline.models.event import TimelineEvent
from core.timeline.models.follow_up import TimelineFollowUp
from core.timeline.repositories.event import EventRepository
from core.timeline.repositories.follow_up import FollowUpRepository


def create_follow_up(
    title="Something will happen",
    text="In Hamburg",
    folder: None | Folder = None,
    user: None | OrgUser = None,
) -> TimelineFollowUp:
    if user is None:
        user = test_helpers.create_raw_org_user(save=True)
    if folder is None:
        folder = test_helpers.create_folder(user=user)["folder"]
    follow_up = TimelineFollowUp.create(
        title=title,
        text=text,
        folder=folder,
        user=user,
        time=timezone.now(),
    )
    fr = DjangoFolderRepository()
    FollowUpRepository().save_follow_up(follow_up, user=user, fr=fr)
    return follow_up


def create_event(
    title="Something will happen",
    text="In Hamburg",
    folder: None | Folder = None,
    user: None | OrgUser = None,
) -> TimelineEvent:
    if user is None:
        user = test_helpers.create_raw_org_user(save=True)
    if folder is None:
        folder = test_helpers.create_folder(user=user)["folder"]
    event = TimelineEvent.create(
        title=title,
        text=text,
        folder=folder,
        user=user,
        time=timezone.now(),
    )
    fr = DjangoFolderRepository()
    EventRepository().save_event(event, user=user, fr=fr)
    return event
