from core.calendar.use_cases.event import (
    create_event,
    delete_event,
    update_event,
)
from core.calendar.use_cases.notification import (
    mark_all_notifications_read,
    mark_notification_read,
)
from core.calendar.use_cases.occurrence import (
    cancel_event_occurrence,
    update_event_occurrence,
)
from core.calendar.use_cases.reminder import (
    create_reminder,
    delete_reminder,
    update_reminder,
)

USECASES = {
    "calendar/create_event": create_event,
    "calendar/update_event": update_event,
    "calendar/delete_event": delete_event,
    "calendar/update_event_occurrence": update_event_occurrence,
    "calendar/cancel_event_occurrence": cancel_event_occurrence,
    "calendar/create_reminder": create_reminder,
    "calendar/update_reminder": update_reminder,
    "calendar/delete_reminder": delete_reminder,
    "calendar/mark_notification_read": mark_notification_read,
    "calendar/mark_all_notifications_read": mark_all_notifications_read,
}
