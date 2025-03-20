import re

import bleach
from django.db import models

from .org import Org


class Note(models.Model):
    @staticmethod
    def create(org: Org, title: str, note: str, order: int, pk=0) -> "Note":
        clean_note = bleach.clean(
            note,
            tags=["a", "p", "strong", "em", "ul", "ol", "li", "s"],
            attributes={"a": ["href"]},
        )
        note_obj = Note(rlc=org, title=title, note=clean_note, order=order)
        if pk:
            note_obj.pk = pk
        return note_obj

    rlc = models.ForeignKey(
        Org, on_delete=models.CASCADE, related_name="notes", blank=True
    )
    title = models.CharField(max_length=200)
    note = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_wide = models.BooleanField(default=False)

    class Meta:
        verbose_name = "ORG_Note"
        verbose_name_plural = "ORG_Notes"
        ordering = ["-order"]

    @property
    def note_with_links(self):
        note = self.note
        note = re.sub(
            r"(http[s]?://\S+)",
            r'<a target="_blank" rel="nofollow" href="\1">\1</a>',
            note,
        )
        return note

    def __str__(self):
        return "rlc: {}; note: {};".format(self.rlc.name, self.title)

    def update_information(
        self,
        new_note: str | None = None,
        new_title: str | None = None,
        new_order: int | None = None,
        is_wide: bool | None = None,
    ):
        if new_note is not None:
            clean_note = bleach.clean(
                new_note,
                tags=["a", "p", "strong", "em", "ul", "ol", "li", "s"],
                attributes={"a": ["href"]},
            )
            self.note = clean_note
        if new_title is not None:
            self.title = new_title
        if new_order is not None:
            self.order = new_order
        if is_wide is not None:
            self.is_wide = is_wide
