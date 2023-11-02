from core.folders.domain.repositories.folder import FolderRepository
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.timeline.repositories.event import EventRepository
from core.timeline.repositories.follow_up import FollowUpRepository

INJECTIONS = {
    FolderRepository: DjangoFolderRepository(),
    FollowUpRepository: FollowUpRepository(),
    EventRepository: EventRepository(),
}
