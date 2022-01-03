from apps.recordmanagement.models import RecordDeletion
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Attaches the deletions to the new record."

    def handle(self, *args, **options):
        for request in RecordDeletion.objects.all():
            new_record = request.old_record.record
            request.record = new_record
            request.save()
