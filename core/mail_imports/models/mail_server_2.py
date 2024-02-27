from uuid import uuid4

from django.db import models


class MI_MailAddress(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True)
    localpart = models.CharField(max_length=100, db_index=True)
    folder_uuid = models.UUIDField()

    class Meta:
        verbose_name = "MI_MailAddress"
        verbose_name_plural = "MI_MailAddress"
        ordering = ["localpart"]

    def __str__(self):
        return "address: {}; folder: {};".format(self.localpart, self.folder_uuid)


# mail server
# abc@mail-import.law-orga.de
# externer mail server nach abrufen mails löschen
