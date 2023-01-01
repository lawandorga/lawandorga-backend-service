from uuid import uuid4

from django.core.management import BaseCommand

from core.questionnaires.models import Questionnaire


class Command(BaseCommand):
    def handle(self, *args, **options):
        qs = Questionnaire.objects.all()
        qs = list(qs)
        for q in qs:
            q.uuid = uuid4()
        Questionnaire.objects.bulk_update(qs, ["uuid"])
