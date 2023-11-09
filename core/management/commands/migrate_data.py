from django.core.management.base import BaseCommand

from core.rlc.models.group import Group


class Command(BaseCommand):
    help = "Migrates Data"

    def handle(self, *args, **options):
        to_delete = []
        for group in list(Group.objects.all().order_by("id")):
            if len(group.keys) == 0 or group.keys is None:
                print(f"{group.pk} - Group {group.name} has no keys")
                if group.members.count() == 0:
                    print("and no members")
                    to_delete.append(group)
        for group in to_delete:
            group.delete()
        # for group in list(Group.objects.all().order_by("id")):
        #     if len(group.keys) > 0:
        #         continue
        #     group.generate_keys()
        #     group.save()
        #     print(f"{group.pk} - Group {group.name} keys generated")
