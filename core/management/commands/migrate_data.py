from django.core.management.base import BaseCommand

from core.rlc.models.group import Group


class Command(BaseCommand):
    help = "Migrates Data"

    def handle(self, *args, **options):
        for group in list(Group.objects.all().order_by("id")):
            group.generate_keys()
            group.save()
            print(f"{group.pk} - Group {group.name} keys generated")
