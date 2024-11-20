from django.core.management.base import BaseCommand

from core.auth.models.org_user import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.rlc.models.org import Org

EMAIL = ""
PK = 0


class Command(BaseCommand):
    def handle(self, *args, **options):
        org = Org.objects.get(pk=PK)
        r = DjangoFolderRepository()
        folders = r.get_list(org.pk)
        user = OrgUser.objects.get(user__email=EMAIL)
        for f in folders:
            total_keys = len(f.keys) + len(f.group_keys) + 1 if f.parent else 0
            if f.has_access(user) and total_keys <= 3:
                print(f.parent_str)
