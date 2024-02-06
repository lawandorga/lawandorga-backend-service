from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from core.models import Org


class Command(BaseCommand):
    def handle(self, *args, **options):
        rlc_id = input("Enter the id of the LC you want to empty: ")
        try:
            rlc = Org.objects.get(pk=rlc_id)
        except (ObjectDoesNotExist, ValueError):
            raise CommandError("No LC was found with this id.")
        empty = input(
            "Do you want to empty LC '{name}' with {records} records, "
            "{files} files and {collab} collab documents? [y/n]: ".format(
                **rlc.get_meta_information()
            )
        )
        empty = True if empty == "y" else False
        if empty:
            rlc.force_empty()
            self.stdout.write("The LC '{}' was emptied.".format(rlc.name))
        else:
            self.stdout.write("No LC was emptied.")
