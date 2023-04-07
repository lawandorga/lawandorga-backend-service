from core.seedwork.repository import Repository
from core.timeline.domain import TimelineEvent


class TimelineEventRepository(Repository):
    IDENTIFIER = "TIMELINE_EVENT"

    @classmethod
    def save(cls, event: TimelineEvent):
        pass
