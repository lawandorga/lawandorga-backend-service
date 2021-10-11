from apps.static.permissions import get_all_permissions_strings
from django.core.management import BaseCommand
from apps.api.models import HasPermission, Permission, UserProfile


class Command(BaseCommand):
    def handle(self, *args, **options):
        for permission in get_all_permissions_strings():
            HasPermission.objects.create(
                permission=Permission.objects.get(name=permission),
                user_has_permission=UserProfile.objects.get(email='dummy@rlcm.de')
            )
