from core.calendar.use_cases.event import (
    create_event,
    delete_event,
    update_event,
)
from core.calendar.use_cases.reminder import (
    create_reminder,
    delete_reminder,
)

USECASES = {
    "calendar/create_event": create_event,
    "calendar/update_event": update_event,
    "calendar/delete_event": delete_event,
    "calendar/create_reminder": create_reminder,
    "calendar/delete_reminder": delete_reminder,
}
