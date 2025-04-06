from core.folders.main import HANDLERS as FOLDER_HANDLERS
from core.org.handlers import HANDLERS as ORG_HANDLERS
from messagebus.domain.bus import Handlers

from .injections import BUS


def combine(*handlers: Handlers) -> Handlers:
    combined: Handlers = {}
    for handler in handlers:
        for event_type, funcs in handler.items():
            if event_type not in combined:
                combined[event_type] = []
            combined[event_type].extend(funcs)
    return combined


HANDLERS: Handlers = combine(FOLDER_HANDLERS, ORG_HANDLERS)


for et in HANDLERS:
    for f in HANDLERS[et]:
        BUS.register_handler(et, f)
