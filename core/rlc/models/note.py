from django.db import models

from .org import Org


class Note(models.Model):
    @staticmethod
    def create(org: Org, title: str, note: str, pk=0) -> "Note":
        note_obj = Note(rlc=org, title=title, note=note)
        if pk:
            note_obj.pk = pk
        return note_obj

    rlc = models.ForeignKey(
        Org, on_delete=models.CASCADE, related_name="notes", blank=True
    )
    title = models.CharField(max_length=200)
    note = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ORG_Note"
        verbose_name_plural = "ORG_Notes"
        ordering = ["-created"]

    def __str__(self):
        return "rlc: {}; note: {};".format(self.rlc.name, self.title)

    def update_information(self, new_note=None, new_title=None):
        if new_note:
            self.note = new_note
        if new_title:
            self.title = new_title
