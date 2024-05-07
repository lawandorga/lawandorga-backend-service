from core.auth.models.org_user import OrgUser
from core.rlc.use_cases.group import invalidate_keys_of
from core.seedwork.message_layer import MessageBusActor
from messagebus.domain.bus import MessageBus


@MessageBus.handler(on=OrgUser.OrgUserLocked)
def handle__org_user_locked(event: OrgUser.OrgUserLocked):
    invalidate_keys_of(MessageBusActor(event.org_pk), event.org_user_uuid)
