from django.core.management.base import BaseCommand

from core.auth.models.org_user import OrgUser
from core.auth.use_cases.keys import check_keys
from core.collab.models.collab import Collab
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.rlc.models.group import Group
from core.rlc.models.org import Org

COLLAB_UUID = ""
GROUP_PK = 0
USER_EMAIL = ""


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.handle_access_bugtest()

    def handle_access_bugtest(self):
        u = OrgUser.objects.get(user__email=USER_EMAIL)
        check_keys(u)

    def handle_collab_bugtest(self):
        def out(x):
            self.stdout.write(x)

        collab = Collab.objects.get(uuid=COLLAB_UUID)
        r = DjangoFolderRepository()
        folder = r.retrieve(collab.org_pk, collab.folder_uuid)
        out(folder)
        org = Org.objects.get(pk=collab.org_pk)
        out(org)
        u = OrgUser.objects.get(user__email=USER_EMAIL)
        g = Group.objects.get(pk=GROUP_PK)

        for k in g.keys:
            if k["owner_uuid"] == str(u.uuid):
                out(k)
