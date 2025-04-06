from core.auth.models.org_user import OrgUser
from core.org.use_cases.group import invalidate_keys_of
from core.seedwork.message_layer import MessageBusActor
from messagebus.domain.bus import Handlers


def handle__org_user_locked(event: OrgUser.OrgUserLocked):
    invalidate_keys_of(MessageBusActor(event.org_pk), event.uuid)


HANDLERS: Handlers = {OrgUser.OrgUserLocked: [handle__org_user_locked]}
