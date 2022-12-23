from core.events.models import Event, Attendance


def event_from_id(__actor, v) -> Event:
    return Event.objects.get(org_id=__actor.org.id, id=v)


def attendance_from_id(__actor, v) -> Attendance:
    return Attendance.objects.get(event__org_id=__actor.org.id, id=v)
