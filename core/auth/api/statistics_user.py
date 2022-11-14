from core.auth.api import schemas
from core.auth.models import StatisticUser
from core.seedwork.api_layer import Router


router = Router()


@router.get(url="data_self/", output_schema=schemas.OutputStatisticsUserData)
def query__data(statistics_user: StatisticUser):
    data = {
        "user": statistics_user,
    }
    return data
