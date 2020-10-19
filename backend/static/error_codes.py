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

ERROR__API__DOWNLOAD__NO_SUCH_KEY = {
    "error_code": "api.download.no_such_key",
    "error_detail": "no such filekey to download",
}

ERROR__API__STORAGE__DELETE__NO_SUCH_KEY = {
    "error_code": "api.storage.delete.no_such_key",
    "error_detail": "no such filekey on storage to delete",
}

ERROR__API__DOWNLOAD__NO_FILE_SPECIFIED = {
    "error_detail": "no file specified",
    "error_code": "api.download.no_file_specified",
}
ERROR__API__UPLOAD__NO_FILE = {
    "error_detail": "no file to upload",
    "error_code": "api.upload.no_file",
}
ERROR__RECORD__RETRIEVE_RECORD__WRONG_RLC = {
    "error_detail": "wrong rlc, the record is in another rlc",
    "error_code": "record.retrieve_record.wrong_rlc",
}
ERROR__RECORD__RECORD__NOT_EXISTING = {
    "error_detail": "the record with the given id does not exist",
    "error_code": "record.record.not_existing",
}
ERROR__RECORD__UPLOAD__NO_FILE_NAME = {
    "error_detail": "no file name",
    "error_code": "record.upload.no_file_name",
}
ERROR__RECORD__UPLOAD__NO_FILE_TYPE = {
    "error_detail": "no file type",
    "error_code": "record.upload.no_file_type",
}
ERROR__RECORD__UPLOAD__NAMES_TYPES_LENGTH_MISMATCH = {
    "error_detail": "the provided names and types are not equal in length",
    "error_code": "record.upload.names_types_length_mismatch",
}

ERROR__API__LOGIN__INVALID_CREDENTIALS = {
    "error_detail": "wrong password or no account with this email",
    "error_code": "api.login.invalid_credentials",
}

ERROR__API__STORAGE__CHECK_FILE_NOT_FOUND = {
    "error_detail": "no such file found, checking error",
    "error_code": "api.storage.check_file_not_found",
}

ERROR__API__STORAGE__DIR_NOT_FOUND = {
    "error_detail": "the directory doesnt exist",
    "error_code": "api.storage.dir_not_found",
}

ERROR__API__STORAGE__DIR_EMPTY = {
    "error_detail": "there are no files in the specified dir",
    "error_code": "api.storage.dir_empty",
}

ERROR__RECORD__MESSAGE__NO_MESSAGE_PROVIDED = {
    "error_detail": "there was no message provided in the request",
    "error_code": "record.message.no_message",
}

ERROR__API__PERMISSION__INSUFFICIENT = {
    "error_detail": "insufficient permission to perform action",
    "error_code": "api.permissions.insufficient",
    "error_status_code": 403,
}

ERROR__RECORD__DOCUMENT__NOT_FOUND = {
    "error_detail": "document not found",
    "error_code": "record.document.not_found",
}

ERROR__RECORD__DOCUMENT__NO_LINKED_RECORD = {
    "error_detail": "no linked record to the document",
    "error_code": "record.document.no_linked_record",
}

ERROR__RECORD__DOCUMENT__NO_TAG_PROVIDED = {
    "error_detail": "no tag provided",
    "error_code": "record.document.no_tag_provided",
}

ERROR__RECORD__DOCUMENT__TAG_NOT_EXISTING = {
    "error_detail": "provided tag does not exist",
    "error_code": "record.document.tag_not_existing",
}

ERROR__RECORD__CLIENT__NOT_EXISTING = {
    "error_detail": "provided tag does not exist",
    "error_code": "record.document.tag_not_existing",
}

ERROR__RECORD__RECORD__COULD_NOT_SAVE = {
    "error_detail": "error at saving the record, contact admin",
    "error_code": "record.record.could_not_save",
}

ERROR__RECORD__PERMISSION__ALREADY_WORKING_ON = {
    "error_detail": "the user is already working on the record",
    "error_code": "record.permission.already_working_on",
}

ERROR__RECORD__PERMISSION__ALREADY_REQUESTED = {
    "error_detail": "already requested a permission for the record",
    "error_code": "record.permission.already_requested",
}

ERROR__API__NO_ACTION_PROVIDED = {
    "error_detail": "no action in request.data provided",
    "error_code": "record.permission.no_action_provided",
}


ERROR__RECORD__PERMISSION__NO_REQUESTS_FOUND = {
    "error_detail": "no requests in database",
    "error_code": "record.permission.no_requests_found",
}

ERROR__API__REGISTER__NO_RLC_PROVIDED = {
    "error_detail": "no rlc was provided",
    "error_code": "api.register.no_rlc_provided",
}

ERROR__API__REGISTER__RLC_NOT_FOUND = {
    "error_detail": "rlc not found",
    "error_code": "api.register.rlc_not_found",
}

ERROR__API__USER__NOT_FOUND = {
    "error_detail": "specified user not found",
    "error_code": "api.user.user_nof_found",
}

ERROR__API__USER__ID_NOT_PROVIDED = {
    "error_detail": "no id provided",
    "error_code": "api.user.id_not_provided",
}

ERROR__API__USER__NOT_SAME_RLC = {
    "error_detail": "you are not from the same rlc",
    "error_code": "api.user.not_same_rlc",
}

ERROR__API__PERMISSION__NOT_FOUND = {
    "error_detail": "given permission not found",
    "error_code": "api.permission.not_found",
}

ERROR__API__EMAIL__NO_EMAIL_PROVIDED = {
    "error_detail": 'no "email" provided',
    "error_code": "api.email.no_email_provided",
}

ERROR__API__USER__ALREADY_FORGOT_PASSWORD = {
    "error_detail": "already sent you an reactivation link",
    "error_code": "api.user.already_forgot_password",
}

ERROR__API__USER__INACTIVE = {
    "error_detail": "account is inactive",
    "error_code": "api.user.inactive",
}

ERROR__API__USER__PASSWORD_RESET_LINK_DOES_NOT_EXIST = {
    "error_detail": "there is no reset password link with this id",
    "error_code": "api.user.password_reset_link_does_not_exist",
}

ERROR__API__USER__NEW_PASSWORD_NOT_PROVIDED = {
    "error_detail": "no new password provided",
    "error_code": "api.user.new_password_not_provided",
}

ERROR__ENV__MISSING_VARIABLE = {
    "error_detail": "a environment variable isn't set",
    "error_code": "env.missing_variable",
}

ERROR__API__MISSING_ARGUMENT = {
    "error_detail": "argument missing (general error)",
    "error_code": "api.missing_argument",
}

ERROR__API__ID_NOT_FOUND = {
    "error_detail": "object with provided id not found",
    "error_code": "api.id_not_found",
}

ERROR__API__ACTION_NOT_VALID = {
    "error_detail": "provided action is not valid",
    "error_code": "api.action_not_valid",
}

ERROR__API__GROUP__GROUP_NOT_FOUND = {
    "error_detail": "no group with this id",
    "error_code": "api.group.not_found",
}

ERROR__API__HAS_PERMISSION__NO_ID_PROVIDED = {
    "error_detail": "no id for hasPermission provided",
    "error_code": "api.has_permission.no_id_provided",
}

ERROR__API__HAS_PERMISSION__NOT_FOUND = {
    "error_detail": "hasPermission not found",
    "error_code": "api.has_permission.not_found",
}

ERROR__API__HAS_PERMISSION__CAN_NOT_CREATE = {
    "error_detail": "cant create hasPermission like that",
    "error_code": "api.has_permission.can_not_create",
}

ERROR__API__HAS_PERMISSION__ALREADY_EXISTING = {
    "error_detail": "hasPermission already exists",
    "error_code": "api.has_permission.already_existing",
}

ERROR__API__GROUP__CAN_NOT_CREATE = {
    "error_detail": "cant create group, not enough data",
    "error_code": "api.group.can_not_create",
}

ERROR__API__GROUP__ALREADY_EXISTING = {
    "error_detail": "group already exists",
    "error_code": "api.group.already_existing",
}

ERROR__API__USER_ACTIVATION__LINK_NOT_FOUND = {
    "error_detail": "activation link not found",
    "error_code": "api.user_activation.link_not_found",
}

ERROR__API__NEW_USER_REQUEST__REQUEST_NOT_FOUND = {
    "error_detail": "new user request for user not found",
    "error_code": "api.new_user_request.request_not_found",
}

ERROR__API__NEW_USER_REQUEST__ID_NOT_PROVIDED = {
    "error_detail": "no new user request id provided",
    "error_code": "api.new_user_request.id_not_provided",
}

ERROR__API__NEW_USER_REQUEST__NO_USER_ACTIVATION_LINK = {
    "error_detail": "no corresponding user activation link",
    "error_code": "api.new_user_request.no_user_activation_link",
}

ERROR__RECORD__ORIGIN_COUNTRY__NOT_FOUND = {
    "error_detail": "origin country not found",
    "error_code": "record.origin_country.not_found",
}

ERROR__API__EMAIL__ALREADY_IN_USE = {
    "error_detail": "email already in use",
    "error_code": "api.email.already_in_use",
}

ERROR__RECORD__RECORD_DELETION__ALREADY_REQUESTED = {
    "error_detail": "deletion of record already requested",
    "error_code": "record.record_deletion.already_requested",
}

ERROR__RECORD__RECORD__ID_NOT_PROVIDED = {
    "error_detail": "record id not provided",
    "error_code": "record.record.id_not_provided",
}

ERROR__API__ID_NOT_PROVIDED = {
    "error_detail": "id not provided",
    "error_code": "api.id_not_provided",
}

ERROR__RECORD__DELETION_REQUEST__NOT_EXISTING = {
    "error_detail": "record deletion request with given id does not exist",
    "error_code": "record.deletion_request.not_existing",
}

ERROR__RECORD__CONSULTANT__NOT_EXISTING = {
    "error_detail": "record couldn't be created, consultant with id not existing",
    "error_code": "record.consultant.not_existing",
}

ERROR__API__USER__NO_PUBLIC_KEY_FOUND = {
    "error_detail": "no public key for user found",
    "error_code": "api.user.no_public_key_found",
}

ERROR__API__USER__NO_PRIVATE_KEY_PROVIDED = {
    "error_detail": "no private key provided",
    "error_code": "api.user.no_private_key_provided",
}

ERROR__API__RLC__NO_PUBLIC_KEY_FOUND = {
    "error_detail": "no public key found",
    "error_code": "api.rlc.no_public_key_found",
}

ERROR__API__RLC__USERS_RLC_KEYS_NOT_FOUND = {
    "error_detail": "users rlc keys not found",
    "error_code": "api.rlc.users_rlc_keys_not_found",
}

ERROR__RECORD__KEY__RECORD_ENCRYPTION_NOT_FOUND = {
    "error_detail": "record encryption keys for user not found",
    "error_code": "record.key.record_encryption_not_found",
}

ERROR__FILES__NO_FILES_TO_UPLOAD = {
    "error_detail": "no files to upload found",
    "error_code": "files.no_files_to_upload",
}

ERROR__API__WRONG_RLC = {"error_detail": "wrong rlc", "error_code": "api.wrong_rlc"}

ERROR__RECORD__PERMISSION__NOT_WORKING_ON = {
    "error_detail": "can't yield, already working on",
    "error_code": "record.permission.not_working_on",
}

ERROR__API__RLC_SETTINGS__WRONG_COUNT = {
    "error_detail": "wrong count of rlc settings",
    "error_code": "api.rlc_settings.wrong_count",
}

ERROR__API__MISSING_KEY_WAIT = {
    "error_detail": "you are missing a key, wait for another user to login",
    "error_code": "api.missing_key.wait",
}

ERROR__FILES__FOLDER_NOT_EXISTING = {
    "error_detail": "folder does not exist",
    "error_code": "api.files.folder_not_existing",
}

ERROR__RECORD__CONSULTANT__NO_PERMISSION = {
    "error_detail": "selected user has no permission to consult",
    "error_code": "api.record.no_consult_permission",
}

ERROR__API__USER__CAN_NOT_CREATE = {
    "error_detail": "can not create user",
    "error_code": "api.user.can_not_create",
}

ERROR__API__NOTIFICATION__UPDATE_INVALID = {
    "error_detail": "update for notification is invalid",
    "error_code": "api.notification.update_invalid",
}

ERROR__API__USER__NO_OWNERSHIP = {
    "error_detail": "user has no ownership of resource",
    "error_code": "api.user.no_ownership",
    "error_status_code": 403,
}

ERROR__API__FIELD_NOT_ALLOWED = {
    "error_detail": "field is not allowed",
    "error_code": "api.field_not_allowed",
}

ERROR__RECORD__TAG__AT_LEAST_ONE = {
    "error_detail": "at least one tag is needed",
    "error_code": "record.tag.at_least_one",
}

ERROR__API__PARAMS_NOT_VALID = {
    "error_detail": "parameters are not valid",
    "error_code": "api.params_not_valid",
}

ERROR__API__ALREADY_PROCESSED = {
    "error_detail": "already processed item",
    "error_code": "api.already_processed",
}

ERROR__API__INVALID_PRIVATE_KEY = {
    "error_detail": "invalid private key",
    "error_code": "api.private_key_invalid",
}

ERROR__API__NOT_AUTHENTICATED = {
    "error_detail": "not authenticated",
    "error_code": "api.not_authenticated",
}

ERROR__API__ALREADY_REQUESTED = {
    "error_detail": "already requested",
    "error_code": "api.already_requested",
}
