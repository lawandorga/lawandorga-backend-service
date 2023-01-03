class MessageBusActor:
    name = "MessageBus"

    def __init__(self, org_pk: int | None):
        self.org_pk: int = org_pk if org_pk else 0

    @property
    def org_id(self) -> int:
        return self.org_pk
