from uuid import UUID

from core.auth.models.org_user import RlcUser
from core.folders.domain.repositories.folder import FolderRepository
from core.timeline.models.event import TimelineEvent


class EventRepository:
    def save_event(
        self, event: TimelineEvent, user: RlcUser, fr: FolderRepository
    ) -> None:
        folder = fr.retrieve(org_pk=user.org_id, uuid=event.folder_uuid)
        event.encrypt(folder=folder, user=user)
        event.save()

    def get_event(
        self, uuid: UUID, user: RlcUser, fr: FolderRepository
    ) -> TimelineEvent:
        event = TimelineEvent.objects.filter(org_id=user.org_id).get(uuid=uuid)
        folder = fr.retrieve(org_pk=user.org_id, uuid=event.folder_uuid)
        event.decrypt(folder=folder, user=user)
        return event

    def delete_event(self, uuid: UUID, user: RlcUser) -> None:
        TimelineEvent.objects.filter(org_id=user.org_id, uuid=uuid).delete()

    def list_events(
        self, folder_uuid: UUID, user: RlcUser, fr: FolderRepository
    ) -> list[TimelineEvent]:
        events = list(
            TimelineEvent.objects.filter(folder_uuid=folder_uuid, org_id=user.org_id)
        )
        folder = fr.retrieve(org_pk=user.org_id, uuid=folder_uuid)
        for event in events:
            event.decrypt(folder=folder, user=user)
        return events
