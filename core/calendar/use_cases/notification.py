from uuid import UUID

from django.utils import timezone

from core.auth.models.org_user import OrgUser
from core.calendar.models import CalendarNotification
from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer import use_case


@use_case
def mark_notification_read(
    __actor: OrgUser,
    notification_uuid: UUID,
) -> None:
    notification = CalendarNotification.objects.get(uuid=notification_uuid)

    if notification.org_user_id != __actor.pk:
        raise DomainError("You can only mark your own notifications as read.")

    notification.mark_read()


@use_case
def mark_all_notifications_read(__actor: OrgUser) -> None:
    CalendarNotification.objects.filter(org_user=__actor, read_at__isnull=True).update(
        read_at=timezone.now()
    )
