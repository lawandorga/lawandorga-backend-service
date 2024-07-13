from django.core.management.base import BaseCommand

from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.rlc.models.org import Org


class Command(BaseCommand):
    def handle(self, *args, **options):
        r = DjangoFolderRepository()
        for org in list(Org.objects.all().order_by("pk")):
            folders = r.get_list(org.pk)
            for f in folders:
                r.save(f)
