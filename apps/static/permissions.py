PERMISSION_CAN_CONSULT = "can_consult"
PERMISSION_VIEW_RECORDS_RLC = "view_records_rlc"
PERMISSION_CAN_ADD_RECORD_RLC = "add_record_rlc"
PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC = "view_records_full_detail_rlc"
PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC = "permit_record_permission_requests_rlc"
PERMISSION_MANAGE_GROUPS_RLC = "manage_groups_rlc"
PERMISSION_MANAGE_USERS = "manage_users"
PERMISSION_VIEW_PERMISSIONS_RLC = "view_permissions_rlc"
PERMISSION_MANAGE_PERMISSIONS_RLC = "manage_permissions_rlc"
PERMISSION_ACCEPT_NEW_USERS_RLC = "accept_new_users_rlc"
PERMISSION_PROCESS_RECORD_DELETION_REQUESTS = "process_record_deletion_requests"
PERMISSION_READ_ALL_FOLDERS_RLC = "read_all_folders_rlc"
PERMISSION_WRITE_ALL_FOLDERS_RLC = "write_all_folders_rlc"
PERMISSION_ACCESS_TO_FILES_RLC = "access_to_files_rlc"
PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC = "manage_folder_permissions_rlc"
PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC = "read_all_collab_documents_rlc"
PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC = "write_all_collab_documents_rlc"
PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC = "manage_collab_document_permissions_rlc"


def get_all_permissions_strings():
    return [
        PERMISSION_CAN_CONSULT,
        PERMISSION_VIEW_RECORDS_RLC,
        PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC,
        PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC,
        PERMISSION_MANAGE_GROUPS_RLC,
        PERMISSION_MANAGE_USERS,
        PERMISSION_VIEW_PERMISSIONS_RLC,
        PERMISSION_MANAGE_PERMISSIONS_RLC,
        PERMISSION_ACCEPT_NEW_USERS_RLC,
        PERMISSION_CAN_ADD_RECORD_RLC,
        PERMISSION_PROCESS_RECORD_DELETION_REQUESTS,
        PERMISSION_ACCESS_TO_FILES_RLC,
        PERMISSION_READ_ALL_FOLDERS_RLC,
        PERMISSION_WRITE_ALL_FOLDERS_RLC,
        PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC,
        PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC,
        PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC,
        PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC,
    ]


def get_all_collab_permissions():
    return [
        PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC,
        PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC,
        PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC,
    ]


def get_all_records_permissions():
    return [
        PERMISSION_CAN_CONSULT,
        PERMISSION_VIEW_RECORDS_RLC,
        PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC,
        PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC,
        PERMISSION_CAN_ADD_RECORD_RLC,
        PERMISSION_PROCESS_RECORD_DELETION_REQUESTS,
    ]


def get_all_files_permissions():
    return [
        PERMISSION_ACCESS_TO_FILES_RLC,
        PERMISSION_READ_ALL_FOLDERS_RLC,
        PERMISSION_WRITE_ALL_FOLDERS_RLC,
        PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC,
    ]


def get_record_encryption_keys_permissions_strings():
    return [
        PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC,
        PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC,
        PERMISSION_MANAGE_PERMISSIONS_RLC,
        PERMISSION_MANAGE_GROUPS_RLC,
    ]


def get_record_encryption_keys_permissions():
    from apps.api.models.permission import Permission

    permissions = []
    for permission_string in get_record_encryption_keys_permissions_strings():
        permissions.append(Permission.objects.get(name=permission_string))
    return permissions
