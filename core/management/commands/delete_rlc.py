from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from core.models import Org


class Command(BaseCommand):
    def handle(self, *args, **options):
        org_id = input("Enter the id of the org you want to delete: ")
        try:
            org = Org.objects.get(pk=org_id)
        except (ObjectDoesNotExist, ValueError):
            raise CommandError("No org was found with this id.")
        delete = input(
            "Do you want to delete org '{name}' with {records} records, "
            "{files} files and {collab} collab documents? [y/n]: ".format(
                **org.get_meta_information()
            )
        )
        delete = True if delete == "y" else False
        if delete:
            org.force_delete()
            self.stdout.write("The org '{}' was deleted.".format(org.name))
        else:
            self.stdout.write("No org was deleted.")
