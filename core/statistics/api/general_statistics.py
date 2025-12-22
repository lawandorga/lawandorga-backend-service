from pydantic import BaseModel

from core.auth.models import StatisticUser
from core.seedwork.api_layer import Router
from core.seedwork.statistics import execute_statement

router = Router()


class OutputRawNumbers(BaseModel):
    records: int
    files: int
    collabs: int
    users: int
    lcs: int


@router.get("raw_numbers/", output_schema=OutputRawNumbers)
def query__raw_numbers(statistics_user: StatisticUser):
    statement = """
           select
           (select count(*) as records from core_datasheet) as records,
           (select count(*) as files from core_file) as files,
           (select count(*) as collab from core_collab as collab),
           (select count(*) as users from core_orguser as users),
           (select count(*) as lcs from core_org as lcs)
           """
    data = execute_statement(statement)
    data = list(
        map(
            lambda x: {
                "records": x[0],
                "files": x[1],
                "collabs": x[2],
                "users": x[3],
                "lcs": x[4],
            },
            data,
        )
    )
    return data[0]
