from core.calendar.use_cases.event import create_event, delete_event, update_event

USECASES = {
    "calendar/create_event": create_event,
    "calendar/update_event": update_event,
    "calendar/delete_event": delete_event,
}
