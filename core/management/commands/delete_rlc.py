from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from core.models import Org


class Command(BaseCommand):
    def handle(self, *args, **options):
        rlc_id = input("Enter the id of the LC you want to delete: ")
        try:
            rlc = Org.objects.get(pk=rlc_id)
        except (ObjectDoesNotExist, ValueError):
            raise CommandError("No LC was found with this id.")
        delete = input(
            "Do you want to delete LC '{name}' with {records} records, "
            "{files} files and {collab} collab documents? [y/n]: ".format(
                **rlc.get_meta_information()
            )
        )
        delete = True if delete == "y" else False
        if delete:
            rlc.force_delete()
            self.stdout.write("The LC '{}' was deleted.".format(rlc.name))
        else:
            self.stdout.write("No LC was deleted.")
