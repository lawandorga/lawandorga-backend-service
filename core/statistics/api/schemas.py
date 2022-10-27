from typing import Any, List, Optional

from pydantic import BaseModel


class InputRecordStats(BaseModel):
    field_1: str
    value_1: str
    field_2: str


class OutputRecordStats(BaseModel):
    error: bool
    label: str
    data: List[tuple[Any, int, int]]


class OutputUserWithMissingRecordKeys(BaseModel):
    user: int
    records: int
    access: int


class OutputRecordClosedStatistic(BaseModel):
    days: Optional[int]
    count: int


class OutputRecordFieldAmount(BaseModel):
    field: str
    amount: int


class OutputRecordsCreatedClosed(BaseModel):
    month: str
    created: int
    closed: int