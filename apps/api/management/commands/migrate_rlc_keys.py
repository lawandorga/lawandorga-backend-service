from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from apps.api.models import Rlc


class Command(BaseCommand):
    def handle(self, *args, **options):
        for rlc in list(Rlc.objects.all().order_by("id")):
            self.stdout.write('{}'.format(rlc.id))
            try:
                keys = rlc.encryption_keys
            except ObjectDoesNotExist:
                self.stdout.write('LC {} has no encryption keys.'.format(rlc.name))
                continue
            rlc.private_key = keys.encrypted_private_key
            rlc.public_key = keys.public_key
