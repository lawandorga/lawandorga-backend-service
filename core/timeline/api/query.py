from core.auth.models.org_user import RlcUser
from core.folders.domain.repositiories.folder import FolderRepository
from core.seedwork.api_layer import Router
from core.seedwork.repository import RepositoryWarehouse
from core.timeline.repository import TimelineEventRepository
from messagebus.domain.store import EventStore

from . import schemas

router = Router()


@router.get(
    "timeline/<uuid:folder_uuid>/",
    output_schema=list[schemas.OutputTimelineEvent],
)
def query_timeline(rlc_user: RlcUser, data: schemas.InputTimelineList):
    tr = TimelineEventRepository(EventStore())
    fr = RepositoryWarehouse.get(FolderRepository)
    folder = fr.retrieve(rlc_user.org_id, data.folder_uuid)
    return tr.list(folder=folder, by=rlc_user)
