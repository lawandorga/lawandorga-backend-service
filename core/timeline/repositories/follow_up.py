from uuid import UUID

from django.utils import timezone

from core.auth.models.org_user import OrgUser
from core.folders.domain.repositories.folder import FolderRepository
from core.timeline.models.follow_up import TimelineFollowUp


class FollowUpRepository:
    def save_follow_up(
        self, follow_up: TimelineFollowUp, user: OrgUser, fr: FolderRepository
    ) -> None:
        folder = fr.retrieve(org_pk=user.org_id, uuid=follow_up.folder_uuid)
        follow_up.encrypt(folder=folder, user=user)
        follow_up.save()

    def get_follow_up(
        self, uuid: UUID, user: OrgUser, fr: FolderRepository
    ) -> TimelineFollowUp:
        follow_up = TimelineFollowUp.objects.filter(org_id=user.org_id).get(uuid=uuid)
        folder = fr.retrieve(org_pk=user.org_id, uuid=follow_up.folder_uuid)
        follow_up.decrypt(folder=folder, user=user)
        return follow_up

    def delete_follow_up(self, uuid: UUID, user: OrgUser) -> None:
        TimelineFollowUp.objects.filter(org_id=user.org_id, uuid=uuid).delete()

    def list_follow_ups_of_user(
        self, user: OrgUser, fr: FolderRepository
    ) -> list[TimelineFollowUp]:
        from core.data_sheets.models import DataSheetUsersEntry

        follow_ups = list(
            TimelineFollowUp.objects.filter(
                org_id=user.org_id, time__lt=timezone.now(), is_done=False
            )
        )
        folders = fr.get_dict(org_pk=user.org_id)
        relevant_follow_ups = []
        for follow_up in follow_ups:
            folder = folders[follow_up.folder_uuid]
            if folder.has_access(owner=user):
                entry = DataSheetUsersEntry.objects.filter(
                    record__folder_uuid=follow_up.folder_uuid
                ).first()
                if entry is not None:
                    if user not in entry.value.all():
                        continue
                follow_up.decrypt(folder=folder, user=user)
                relevant_follow_ups.append(follow_up)
        return relevant_follow_ups

    def list_follow_ups(
        self, folder_uuid: UUID, user: OrgUser, fr: FolderRepository
    ) -> list[TimelineFollowUp]:
        follow_ups = list(
            TimelineFollowUp.objects.filter(folder_uuid=folder_uuid, org_id=user.org_id)
        )
        folder = fr.retrieve(org_pk=user.org_id, uuid=folder_uuid)
        for follow_up in follow_ups:
            follow_up.decrypt(folder=folder, user=user)
        return follow_ups
