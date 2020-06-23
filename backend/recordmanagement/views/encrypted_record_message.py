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
from rest_framework.views import APIView
from rest_framework.response import Response

from backend.recordmanagement import models, serializers
from backend.static import error_codes
from backend.api.errors import CustomError
from backend.static.emails import EmailSender
from backend.static.middleware import get_private_key_from_request
from backend.static.encryption import AESEncryption


class EncryptedRecordMessageViewSet(viewsets.ModelViewSet):
    queryset = models.EncryptedRecordMessage.objects.all()
    serializer_class = serializers.EncryptedRecordMessageSerializer


class EncryptedRecordMessageByRecordViewSet(APIView):
    def post(self, request, id):
        if 'message' not in request.data or request.data['message'] == '':
            raise CustomError(error_codes.ERROR__RECORD__MESSAGE__NO_MESSAGE_PROVIDED)
        users_private_key = get_private_key_from_request(request)

        try:
            e_record = models.EncryptedRecord.objects.get(pk=id)
        except Exception as e:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__NOT_EXISTING)
        if not e_record.user_has_permission(request.user):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        # to replace
        record_key = e_record.get_decryption_key(request.user, users_private_key)
        message = AESEncryption.encrypt(request.data['message'], record_key)

        record_message = models.EncryptedRecordMessage(sender=request.user, message=message, record=e_record)
        record_message.save()
        # until here
        # replace it with this
        # models.EncryptedRecordMessage.objects.create_encrypted_record_message(sender=request.user, message=message,
        #                                                                       record=e_record,
        #                                                                       senders_private_key=users_private_key)
        #

        EmailSender.send_record_new_message_notification_email(e_record)
        return Response(serializers.EncryptedRecordMessageSerializer(record_message).get_decrypted_data(record_key))

    def get(self, request, id):
        pass
