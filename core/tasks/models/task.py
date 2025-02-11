from datetime import datetime
from uuid import uuid4

from django.db import models

from ...auth.models import OrgUser


class Task(models.Model):
    @classmethod
    def create(
        cls,
        __actor: OrgUser,
        assignee_id: int,
        title: str,
        description: str,
        page_url: str,
        deadline: datetime,
    ):
        task = cls(
            creator=__actor,
            title=title,
            description=description,
            page_url=page_url,
            deadline=deadline,
        )

        task.assignee = OrgUser.objects.get(id=assignee_id)
        return task

    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True, editable=False)
    creator = models.ForeignKey(
        OrgUser, on_delete=models.CASCADE, related_name="creator"
    )
    assignee = models.ForeignKey(
        OrgUser, on_delete=models.CASCADE, related_name="assignee"
    )
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(default="", null=True, blank=True)
    page_url = models.CharField(max_length=255, blank=True)
    is_done = models.BooleanField(default=False)
    deadline = models.DateTimeField(default=datetime.now, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_as_done(self):
        self.is_done = True

    def __str__(self) -> str:
        return self.title

    @property
    def creator_id(self):
        return self.creator.pk

    @property
    def assignee_id(self):
        return self.assignee.pk
