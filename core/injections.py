from core.auth.domain.user_key import UserKey
from core.auth.models.org_user import OrgUser
from core.auth.models.user import UserProfile
from core.collab.repositories.collab import CollabRepository
from core.data_sheets.models.data_sheet import DataSheetRepository
from core.files_new.models.file import FileRepository
from core.folders.domain.repositories.folder import FolderRepository
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.other.models.logged_path import LoggedPath
from core.questionnaires.models.questionnaire import QuestionnaireRepository
from core.records.models.record import RecordRepository
from core.seedwork.use_case_layer.callbacks import CallbackContext
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


def handle_events(context: CallbackContext, collector: EventCollector):
    if not context.success:
        return
    while event := collector.pop():
        save_event(event)
        BUS.handle(event)


def log_usecase(context: CallbackContext):
    if hasattr(context.actor, "user") and isinstance(context.actor.user, UserProfile):
        LoggedPath.objects.create(
            user=context.actor.user,
            path=context.fn_name,
            status=200 if context.success else 400,
            method="USECASE",
        )


def get_key(__actor: OrgUser) -> UserKey:
    # injecting the UserKey only works if the usecase itself
    # already has OrgUser as an actor
    return __actor._get_user_key()


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
    UserKey: get_key,
}

CALLBACKS = [
    handle_events,
    log_usecase,
]
