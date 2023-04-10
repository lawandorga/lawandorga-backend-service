from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from seedwork.types import JsonDict


class Event(BaseModel):
    aggregate_uuid: Optional[UUID] = None
    position: Optional[int] = None
    time: Optional[datetime] = None

    def __str__(self):
        return self.action

    @property
    def _name(self) -> str:
        return self.__class__.__qualname__

    @property
    def _qualname_splits(self) -> list[str]:
        splits = self._name.split(".")
        if len(splits) != 2:
            raise ValueError(
                f"Event {self._name} is not nested correctly. Make sure it inside a class."
            )
        return splits

    @property
    def action(self) -> str:
        return self._qualname_splits[1]

    @property
    def aggregate_name(self) -> str:
        return self._qualname_splits[0]

    @property
    def data(self) -> JsonDict:
        return self._clean_data(self.dict())

    @property
    def metadata(self) -> JsonDict:
        return {}

    def set_aggregate_uuid(self, uuid: UUID) -> None:
        self.aggregate_uuid = uuid

    def set_position(self, position: int) -> None:
        self.position = position

    def set_time(self, time: datetime) -> None:
        self.time = time

    @classmethod
    def _get_name(cls) -> str:
        parts = cls.__qualname__.split(".")
        if len(parts) < 2:
            raise ValueError(f"The Event '{cls}' is not nested correctly.")
        return f"{parts[-2]}.{parts[-1]}"

    @staticmethod
    def _clean_data(data: dict) -> JsonDict:
        new_data: JsonDict = {}
        for key, item in data.items():
            assert isinstance(key, str)
            if key == "aggregate_uuid":
                continue
            elif isinstance(item, UUID):
                new_data[key] = str(item)
            elif (
                isinstance(item, str)
                or isinstance(item, int)
                or isinstance(item, float)
                or isinstance(item, bool)
            ):
                new_data[key] = item
            elif isinstance(item, dict):
                new_data[key] = Event._clean_data(item)
            elif item is None:
                continue
            else:
                raise ValueError("unknown type in event data can not be put in data")
        return new_data
