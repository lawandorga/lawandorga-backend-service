from django.core.management.base import BaseCommand
from apps.api.models import Rlc


class Command(BaseCommand):
    def handle(self, *args, **options):
        for rlc in list(Rlc.objects.all().order_by('id')):
            print(rlc.get_meta_information())
