from apps.recordmanagement.models import RecordDeletion
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        for rd in RecordDeletion.objects.all():
            record = getattr(rd, 'record', None)
            user1 = getattr(rd, 'requested_by', None)
            user2 = getattr(rd, 'processed_by', None)
            rlc1 = record.template.rlc.id if record else 0
            rlc2 = user1.rlc.id if user1 else 0
            rlc3 = user2.rlc.id if user2 else 0
            rlc1 = rlc1 or rlc2 or rlc3
            rlc2 = rlc2 or rlc1 or rlc3
            rlc3 = rlc3 or rlc1 or rlc2
            if rlc1 != rlc2 or rlc2 != rlc3:
                print(rd)
