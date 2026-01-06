from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from core.auth.models import UserProfile
from core.management.commands.empty_rlc import force_empty
from core.models import Org


def force_delete(org: Org):
    user_ids = []
    for u in org.users.all():
        user_ids.append(u.user_id)
        u.delete()
    for p in list(UserProfile.objects.filter(id__in=user_ids)):
        p.delete()
    org.delete()


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
            force_empty(org)
            force_delete(org)
            self.stdout.write("The org '{}' was deleted.".format(org.name))
        else:
            self.stdout.write("No org was deleted.")
