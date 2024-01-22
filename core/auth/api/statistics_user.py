from pydantic import BaseModel, ConfigDict

from core.auth.models import StatisticUser
from core.seedwork.api_layer import Router

router = Router()


class OutputStatisticsUser(BaseModel):
    id: int
    user_id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class OutputStatisticsUserData(BaseModel):
    user: OutputStatisticsUser


@router.get(url="data_self/", output_schema=OutputStatisticsUserData)
def query__data(statistics_user: StatisticUser):
    data = {
        "user": statistics_user,
    }
    return data
