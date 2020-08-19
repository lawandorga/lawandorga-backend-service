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

import string
import secrets
from django.utils.crypto import get_random_string


def generate_random_string(length=32):
    unique_id = get_random_string(length)
    return unique_id


def generate_secure_random_string(length=64):
    """
    Generate a secure random string of letters, digits and special characters
    :param length: length of random string, 64 rsa encrypted results still in 256 bytes
    """
    password_characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(password_characters) for i in range(length))
