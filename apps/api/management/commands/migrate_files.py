from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from apps.files.models import File


class Command(BaseCommand):
    def handle(self, *args, **options):
        for file in list(File.objects.filter(file=None).order_by('id')):
            print(file.id)
            f = default_storage.open(file.get_encrypted_file_key())
            f.name = f.name.split('/')[-1]
            file.file = f
            file.save()
