from uuid import uuid4

from django.db import models

from ...auth.models import UserProfile


class Todo(models.Model):
    @classmethod
    def create(
        cls,
        creator: UserProfile,
        assignee: UserProfile,
        title: str,
        description: str,
        page_url: str,
        updated_at: str,
    ):
        todo = cls(
            creator=creator,
            assignee=assignee,
            title=title,
            description=description,
            page_url=page_url,
        )

        if updated_at:
            todo.updated_at = updated_at

    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True, editable=False)
    creator = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="creator"
    )
    assignee = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="assignee"
    )
    title = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    page_url = models.CharField(max_length=255, blank=True)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_as_done(self):
        self.is_done = True
