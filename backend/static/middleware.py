#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
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

from backend.static.encryption import get_bytes_from_string_or_return_bytes


def get_private_key_from_request(request):
    # TODO: ! encryption: raise error if no private key? only call when really needed
    private_key = request.META.get('HTTP_PRIVATEKEY')
    private_key = private_key.replace('\\n', '\n')
    if isinstance(private_key, str):
        private_key = get_bytes_from_string_or_return_bytes(private_key)
    return private_key
