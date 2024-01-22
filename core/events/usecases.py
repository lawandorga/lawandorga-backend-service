from core.events.use_cases.events import (
    create_event,
    delete_event,
    reset_calendar_uuid,
    update_event,
)

USECASES = {
    "events/create_event": create_event,
    "events/update_event": update_event,
    "events/delete_event": delete_event,
    "events/reset_calendar_url": reset_calendar_uuid,
}
