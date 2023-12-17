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

INJECTIONS = {
    FolderRepository: DjangoFolderRepository(),
    FollowUpRepository: FollowUpRepository(),
    EventRepository: EventRepository(),
    DataSheetRepository: DataSheetRepository(),
    FileRepository: FileRepository(),
    QuestionnaireRepository: QuestionnaireRepository(),
    UploadLinkRepository: UploadLinkRepository(),
    RecordRepository: RecordRepository(),
    CollabRepository: CollabRepository(),
}
