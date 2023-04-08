from datetime import datetime
from typing import Optional, Protocol

from seedwork.types import JsonDict


class Message(Protocol):
    @property
    def stream_name(self) -> str:
        ...

    @property
    def action(self) -> str:
        ...

    @property
    def data(self) -> JsonDict:
        ...

    @property
    def metadata(self) -> JsonDict:
        ...

    @property
    def position(self) -> Optional[int]:
        ...

    @property
    def time(self) -> Optional[datetime]:
        ...

    def set_position(self, position: int) -> None:
        ...

    def set_time(self, time: datetime) -> None:
        ...
