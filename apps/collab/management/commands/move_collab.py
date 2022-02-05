from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from apps.collab.models import CollabDocument, TextDocument


class Command(BaseCommand):
    def handle(self, *args, **options):
        for collab_document in list(CollabDocument.objects.all().order_by('id')):
            print(collab_document.pk)
            cb: CollabDocument = collab_document
            cb.new_rlc = cb.rlc
            cb.new_created = cb.created
            cb.new_creator = cb.creator
            cb.new_id = cb.id
            cb.save()
