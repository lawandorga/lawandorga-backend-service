from django.core.management.base import BaseCommand
from apps.api.models import Group


class Command(BaseCommand):
    def handle(self, *args, **options):
        for g in Group.objects.all():
            g.description = '{}\n\nNote:\n{}'.format(g.description, g.note)
            g.save()
