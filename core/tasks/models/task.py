import re
from datetime import datetime
from typing import Optional
from uuid import uuid4

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.auth.models import OrgUser
from core.seedwork.domain_layer import DomainError


def validate_tags(tags: list[str]) -> str:
    if len(tags) > 5:
        raise DomainError("A task can have at most 5 tags.")
    for tag in tags:
        if len(tag) > 100:
            raise DomainError("A tag can have at most 100 characters.")
        if not re.match(r"^[a-zA-Z0-9 ]*$", tag):
            raise DomainError("Tags can only contain letters, numbers, and spaces.")
    return "|".join(tags)


class Task(models.Model):
    @classmethod
    def create(
        cls,
        __actor: OrgUser,
        assignee_ids: list[int],
        title: str,
        description: str,
        page_url: str,
        deadline: Optional[datetime] = None,
        tags: Optional[list[str]] = None,
        save: bool = False,
    ):
        task = cls(
            creator=__actor,
            title=title,
            description=description,
            page_url=page_url,
            deadline=deadline,
        )
        if tags:
            task.tags = validate_tags(tags)
        if save:
            task.save()
            task.assignees.set(OrgUser.objects.filter(id__in=assignee_ids))
        return task

    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True, editable=False)
    creator = models.ForeignKey(
        OrgUser, on_delete=models.CASCADE, related_name="created_tasks"
    )
    assignees = models.ManyToManyField(
        OrgUser, related_name="assigned_tasks", blank=True
    )
    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_URGENT = "urgent"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
        (PRIORITY_URGENT, "Urgent"),
    ]
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM
    )
    progress = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(default="", null=True, blank=True)
    page_url = models.CharField(max_length=255, blank=True)
    deadline = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comments = models.JSONField(default=list, blank=True)
    tags = models.CharField(blank=True, max_length=512)

    class Meta:
        verbose_name = "TAS_Task"
        verbose_name_plural = "TAS_Tasks"

    @property
    def creator_id(self):
        return self.creator.pk

    @property
    def creator_name(self):
        return self.creator.name

    @property
    def assignee_ids(self):
        return list(self.assignees.values_list("id", flat=True))

    @property
    def assignee_names(self):
        return list(self.assignees.values_list("user__name", flat=True))

    @property
    def is_done(self):
        return self.progress == 100

    @property
    def tags_as_list(self):
        if not self.tags:
            return []
        return self.tags.split("|")

    def __str__(self) -> str:
        return self.title
