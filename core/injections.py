from core.collab.repositories.collab import CollabRepository
from core.data_sheets.models.data_sheet import DataSheetRepository
from core.files_new.models.file import FileRepository
from core.folders.domain.repositories.folder import FolderRepository
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.questionnaires.models.questionnaire import QuestionnaireRepository
from core.records.models.record import RecordRepository
from core.timeline.repositories.event import EventRepository
from core.timeline.repositories.follow_up import FollowUpRepository
from core.upload.models.upload import UploadLinkRepository
from messagebus.domain.bus import MessageBus
from messagebus.domain.collector import EventCollector
from messagebus.domain.event import Event
from messagebus.domain.store import EventStore

fr = DjangoFolderRepository()
fur = FollowUpRepository()
er = EventRepository()
dsr = DataSheetRepository()
qr = QuestionnaireRepository()
ur = UploadLinkRepository()
rr = RecordRepository()
cr = CollabRepository()
fir = FileRepository()

BUS = MessageBus()
BUS.run_checks()


def save_event(event: Event):
    store: EventStore = EventStore()  # type: ignore
    store.append(event.stream_name, [event])


def handle_events(collector: EventCollector):
    while event := collector.pop():
        save_event(event)
        BUS.handle(event)


INJECTIONS = {
    FolderRepository: fr,
    FollowUpRepository: fur,
    EventRepository: er,
    DataSheetRepository: dsr,
    FileRepository: fir,
    QuestionnaireRepository: qr,
    UploadLinkRepository: ur,
    RecordRepository: rr,
    CollabRepository: cr,
    EventCollector: lambda: EventCollector(),
}

CALLBACKS = [
    handle_events,
]
