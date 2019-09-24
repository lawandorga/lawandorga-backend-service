#  rlcapp - record and organization management software for refugee law clinics
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

from django.core.validators import RegexValidator
import re

PHONE_REGEX = '^\+{0,2}\d{6,15}$'
RECORD_STORAGE_REGEX = '^rlcs\/\d+\/records\/\d+\/?$'

phone_regex = RegexValidator(regex=r'{}'.format(PHONE_REGEX),
                             message="Phone number must be entered "
                                     "in the format: Up to 15 digits allowed.")


def is_storage_folder_of_record(dir: str):
    return bool(re.match(RECORD_STORAGE_REGEX, dir))


def is_phone_number(phone_number: str):
    return bool(re.match(PHONE_REGEX, phone_number.replace(' ', '')))
