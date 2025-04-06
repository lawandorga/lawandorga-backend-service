from typing import Any, Protocol

from pydantic import BaseModel

from seedwork.types import JsonDict


class Message(Protocol):
    # inspired by: http://docs.eventide-project.org/user-guide/message-db/anatomy.html#messages-table
    # stream names: http://docs.eventide-project.org/user-guide/stream-names/#parts

    @property
    def action(self) -> str: ...

    @property
    def data(self) -> JsonDict: ...

    @property
    def metadata(self) -> JsonDict: ...

    def add_to_metadata(self, key: str, value: Any) -> None: ...


class DomainMessage(BaseModel):
    action: str
    data: dict
    metadata: dict = {}

    def add_to_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value
