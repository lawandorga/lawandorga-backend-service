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

import os
from backend.recordmanagement.models import Record
from backend.static.regex_validators import is_storage_folder_of_record

STORAGE_FOLDER_PROFILE_PICTURES = "profile_pictures/"

# TODO refactor this into classes, 1 storage folders specific, 1 general filename manipulation


def get_storage_folder_record_document(rlc_id, record_id):
    return 'rlcs/' + str(rlc_id) + '/records/' + str(record_id) + '/'


def get_storage_folder_encrypted_record_document(rlc_id, record_id):
    return 'rlcs/' + str(rlc_id) + '/encrypted_records/' + str(record_id) + '/'


def get_storage_base_files_folder(rlc_id):
    return 'rlcs/' + str(rlc_id) + '/'


def get_temp_storage_path(filename):
    return os.path.join('temp', filename)


def get_temp_storage_folder():
    return 'temp'


def combine_s3_folder_with_filename(s3_folder, filename):
    return os.path.join(s3_folder, filename)


def get_filename_from_full_path(filepath):
    return filepath[filepath.rindex('/')+1:]


def user_has_permission(file_dir, user):
    """
    checks if the user has permission for the given file_dir
    :param file_dir: string, file_dir for which it is to check if the user has permission
    :param user: UserProfile, the user which is to check
    :return: bool, true if the user has the permissions
    """
    if is_storage_folder_of_record(file_dir):
        id = file_dir.strip('/').split('/')[-1]
        try:
            record = Record.objects.get(pk=id)
        except Exception as e:
            return False
        return record.user_has_permission(user)
    return False
