from datetime import datetime
from typing import Optional, Protocol

from pydantic import BaseModel

from seedwork.types import JsonDict


class Message(Protocol):
    # inspired by: http://docs.eventide-project.org/user-guide/message-db/anatomy.html#messages-table
    # stream names: http://docs.eventide-project.org/user-guide/stream-names/#parts

    @property
    def action(self) -> str:
        pass

    @property
    def data(self) -> JsonDict:
        pass

    @property
    def metadata(self) -> JsonDict:
        pass

    @property
    def position(self) -> Optional[int]:
        pass

    @property
    def time(self) -> Optional[datetime]:
        pass

    def set_position(self, position: int) -> None:
        pass

    def set_time(self, time: datetime) -> None:
        pass


class DomainMessage(BaseModel):
    action: str
    data: dict
    metadata: dict = {}
    position: Optional[int] = None
    time: Optional[datetime] = None

    def set_position(self, position: int) -> None:
        self.position = position

    def set_time(self, time: datetime) -> None:
        self.time = time
