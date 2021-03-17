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


# TODO refactor this into classes, 1 storage folders specific, 1 general filename manipulation


def get_storage_folder_record_document(rlc_id: int, record_id: int) -> str:
    return "rlcs/" + str(rlc_id) + "/records/" + str(record_id) + "/"


def get_storage_folder_encrypted_record_document(rlc_id: int, record_id: int) -> str:
    return "rlcs/" + str(rlc_id) + "/encrypted_records/" + str(record_id) + "/"


def get_storage_base_files_folder(rlc_id: int) -> str:
    return "rlcs/" + str(rlc_id) + "/"


def get_temp_storage_path(filename) -> str:
    return os.path.join("temp", filename)


def get_temp_storage_folder() -> str:
    return "temp"


def combine_s3_folder_with_filename(s3_folder, filename):
    return os.path.join(s3_folder, filename)


def get_filename_from_full_path(filepath: str) -> str:
    return filepath[filepath.rindex("/") + 1 :]
