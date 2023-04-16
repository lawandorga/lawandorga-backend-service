from typing import Any, Protocol

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

    def add_to_metadata(self, key: str, value: Any) -> None:
        pass


class DomainMessage(BaseModel):
    action: str
    data: dict
    metadata: dict = {}

    def add_to_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value
