from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from apps.core.models import UserProfile


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in list(UserProfile.objects.all().order_by("id")):
            self.stdout.write('{}'.format(user.id))
            try:
                keys = user.encryption_keys
            except ObjectDoesNotExist:
                self.stdout.write('User {} has no encryption keys.'.format(user.email))
                continue
            try:
                rlc_user = user.rlc_user
            except ObjectDoesNotExist:
                self.stdout.write('User {} has no rlc user.'.format(user.email))
                continue
            rlc_user.private_key = keys.private_key
            rlc_user.public_key = keys.public_key
            rlc_user.is_private_key_encrypted = keys.private_key_encrypted
            rlc_user.save()
