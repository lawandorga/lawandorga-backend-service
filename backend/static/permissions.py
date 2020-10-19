#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>

from backend.api.models import Permission

PERMISSION_CAN_CONSULT = "can_consult"
PERMISSION_VIEW_RECORDS_RLC = "view_records_rlc"
PERMISSION_CAN_ADD_RECORD_RLC = "add_record_rlc"
PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC = "view_records_full_detail_rlc"
PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC = (
    "permit_record_permission_requests_rlc"
)
PERMISSION_VIEW_FULL_USER_DETAIL_RLC = "view_full_user_detail_own_rlc"
PERMISSION_VIEW_FULL_USER_DETAIL_OVERALL = "view_full_user_detail_overall"
PERMISSION_MANAGE_GROUPS_RLC = "manage_groups_rlc"
PERMISSION_MANAGE_GROUP = "manage_group"
PERMISSION_ADD_GROUP_RLC = "add_group_rlc"
PERMISSION_VIEW_PERMISSIONS_RLC = "view_permissions_rlc"
PERMISSION_MANAGE_PERMISSIONS_RLC = "manage_permissions_rlc"
PERMISSION_ACCEPT_NEW_USERS_RLC = "accept_new_users_rlc"
PERMISSION_ACTIVATE_INACTIVE_USERS_RLC = "activate_inactive_users_rlc"
PERMISSION_PROCESS_RECORD_DELETION_REQUESTS = "process_record_deletion_requests"
PERMISSION_READ_ALL_FOLDERS_RLC = "read_all_folders_rlc"
PERMISSION_WRITE_ALL_FOLDERS_RLC = "write_all_folders_rlc"
PERMISSION_ACCESS_TO_FILES_RLC = "access_to_files_rlc"
PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC = "manage_folder_permissions_rlc"
PERMISSION_PROCESS_RECORD_DOCUMENT_DELETION_REQUESTS = (
    "process_record_document_deletion_requests"
)


def get_all_permissions_strings():
    return [
        PERMISSION_CAN_CONSULT,
        PERMISSION_VIEW_RECORDS_RLC,
        PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC,
        PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC,
        PERMISSION_VIEW_FULL_USER_DETAIL_RLC,
        PERMISSION_VIEW_FULL_USER_DETAIL_OVERALL,
        PERMISSION_MANAGE_GROUPS_RLC,
        PERMISSION_MANAGE_GROUP,
        PERMISSION_ADD_GROUP_RLC,
        PERMISSION_VIEW_PERMISSIONS_RLC,
        PERMISSION_MANAGE_PERMISSIONS_RLC,
        PERMISSION_ACCEPT_NEW_USERS_RLC,
        PERMISSION_ACTIVATE_INACTIVE_USERS_RLC,
        PERMISSION_CAN_ADD_RECORD_RLC,
        PERMISSION_PROCESS_RECORD_DELETION_REQUESTS,
        PERMISSION_ACCESS_TO_FILES_RLC,
        PERMISSION_READ_ALL_FOLDERS_RLC,
        PERMISSION_WRITE_ALL_FOLDERS_RLC,
        PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC,
        PERMISSION_PROCESS_RECORD_DOCUMENT_DELETION_REQUESTS,
    ]


def get_record_encryption_keys_permissions_strings():
    return [
        PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC,
        PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC,
        PERMISSION_MANAGE_PERMISSIONS_RLC,
        PERMISSION_MANAGE_GROUPS_RLC,
    ]


def get_record_encryption_keys_permissions():
    permissions = []
    for permission_string in get_record_encryption_keys_permissions_strings():
        permissions.append(Permission.objects.get(name=permission_string))
    return permissions
