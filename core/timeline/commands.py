from core.timeline.usecases.event import create_event, delete_event, update_event
from core.timeline.usecases.follow_up import (
    create_follow_up,
    delete_follow_up,
    set_follow_up_as_done,
    update_follow_up,
)

COMMANDS = {
    "timeline/create_follow_up": create_follow_up,
    "timeline/update_follow_up": update_follow_up,
    "timeline/delete_follow_up": delete_follow_up,
    "timeline/set_follow_up_as_done": set_follow_up_as_done,
    "timeline/create_event": create_event,
    "timeline/update_event": update_event,
    "timeline/delete_event": delete_event,
}
