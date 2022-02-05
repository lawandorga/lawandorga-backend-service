from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from apps.collab.models import CollabDocument


class Command(BaseCommand):
    def handle(self, *args, **options):
        for collab_document in list(CollabDocument.objects.all().order_by('id')):
            cb: CollabDocument = collab_document
            text_document = collab_document.text
