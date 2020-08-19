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

from rest_framework import viewsets
from rest_framework.response import Response

from backend.api.errors import CustomError
from backend.recordmanagement.models import PoolConsultant, PoolRecord, RecordEncryption
from backend.recordmanagement.serializers import PoolConsultantSerializer
from backend.static import error_codes
from backend.static.permissions import PERMISSION_CAN_CONSULT


class PoolConsultantViewSet(viewsets.ModelViewSet):
    queryset = PoolConsultant.objects.all()
    serializer_class = PoolConsultantSerializer

    def create(self, request, *args, **kwargs):
        # check permissions (can consult)
        user = request.user
        if not user.has_permission(PERMISSION_CAN_CONSULT, for_rlc=user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        if PoolRecord.objects.filter(record__from_rlc=user.rlc).count() >= 1:
            entry = (
                PoolRecord.objects.filter(record__from_rlc=user.rlc)
                .order_by("enlisted")
                .first()
            )

            record = entry.record
            record.working_on_record.remove(entry.yielder)
            record.working_on_record.add(user)
            record.save()

            RecordEncryption.objects.filter(record=record, user=entry.yielder).delete()
            new_keys = RecordEncryption(
                user=user,
                record=record,
                encrypted_key=user.rsa_encrypt(entry.record_key),
            )
            new_keys.save()

            entry.delete()
            return Response({"action": "matched"})
        else:
            pool_consultant = PoolConsultant(consultant=user)
            pool_consultant.save()

            number_of_entries = PoolConsultant.objects.filter(consultant=user).count()
            return_val = PoolConsultantSerializer(pool_consultant).data
            return_val.update(
                {"action": "created", "number_of_enlistings": number_of_entries}
            )
            return Response(return_val)
