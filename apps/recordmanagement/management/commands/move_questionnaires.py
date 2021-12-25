from apps.recordmanagement.models import Questionnaire
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Attaches the messages to the new record."

    def handle(self, *args, **options):
        for questionnaire in Questionnaire.objects.all():
            new_record = questionnaire.old_record.record
            questionnaire.record = new_record
            questionnaire.save()
