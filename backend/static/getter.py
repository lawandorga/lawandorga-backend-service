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

from backend.api.errors import CustomError
from backend.recordmanagement.models.encrypted_record import EncryptedRecord
from backend.static import error_codes
from backend.static import permissions


def get_e_record(user, e_record_id):
    if not user.has_permission(
        permissions.PERMISSION_VIEW_RECORDS_RLC, for_rlc=user.rlc
    ):
        raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
    try:
        e_record = EncryptedRecord.objects.get(pk=e_record_id)
    except Exception as e:
        raise CustomError(error_codes.ERROR__RECORD__RECORD__NOT_EXISTING)
    return e_record
