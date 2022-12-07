import uuid

from django.core.management.base import BaseCommand

from core.auth.models import RlcUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = list(RlcUser.objects.all())
        for u in users:
            u.uuid = uuid.uuid4()
        RlcUser.objects.bulk_update(users, fields=["slug"])
