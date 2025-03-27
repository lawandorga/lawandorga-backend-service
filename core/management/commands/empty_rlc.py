from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from core.models import Org


class Command(BaseCommand):
    def handle(self, *args, **options):
        org_id = input("Enter the id of the org you want to empty: ")
        try:
            org = Org.objects.get(pk=org_id)
        except (ObjectDoesNotExist, ValueError):
            raise CommandError("No org was found with this id.")
        empty = input(
            "Do you want to empty org '{name}' with {records} records, "
            "{files} files and {collab} collab documents? [y/n]: ".format(
                **org.get_meta_information()
            )
        )
        empty = True if empty == "y" else False
        if empty:
            org.force_empty()
            self.stdout.write("The org '{}' was emptied.".format(org.name))
        else:
            self.stdout.write("No org was emptied.")
