from django.core.management.base import BaseCommand
from backend.static.permissions import PERMISSION_MANAGE_GROUP, PERMISSION_MANAGE_GROUPS_RLC
from backend.api.models import Permission, HasPermission


class Command(BaseCommand):
    def replace_permission(self, delete, replacement):
        for p in HasPermission.objects.filter(permission=delete):
            data = {
                'permission': replacement,
                'user_has_permission': p.user_has_permission,
                'group_has_permission': p.group_has_permission,
                'rlc_has_permission': p.rlc_has_permission
            }
            if not HasPermission.objects.filter(**data):
                HasPermission.objects.create(**data)

    def handle(self, *args, **options):
        # manage_groups_rlc / manage_group
        permission_to_delete = Permission.objects.get(name=PERMISSION_MANAGE_GROUP)
        permission_to_replace = Permission.objects.get(name=PERMISSION_MANAGE_GROUPS_RLC)
        self.replace_permission(permission_to_delete, permission_to_replace)
        permission_to_delete.delete()
        # manage_users / view_full_user_detail_overall && manage_users / view_full_user_detail_own_rlc
        permission_to_replace = Permission.objects.get(name='manage_users')
        permission_to_delete = Permission.objects.get(name='view_full_user_detail_overall')
        self.replace_permission(permission_to_delete, permission_to_replace)
        permission_to_delete.delete()
        permission_to_delete = Permission.objects.get(name='view_full_user_detail_own_rlc')
        self.replace_permission(permission_to_delete, permission_to_replace)
        permission_to_delete.delete()
        # manage_groups_rlc / add_group
        permission_to_delete = Permission.objects.get(name='add_group')
        permission_to_replace = Permission.objects.get(name='manage_groups_rlc')
        self.replace_permission(permission_to_delete, permission_to_replace)
        permission_to_delete.delete()
        #
        Permission.objects.get(name='activate_inactive_users').delete()
        Permission.objects.get(name='process_record_document_deletion_requests').delete()
