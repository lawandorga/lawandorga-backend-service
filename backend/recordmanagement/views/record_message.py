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


from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from backend.recordmanagement import models, serializers
from backend.static import error_codes
from backend.api.errors import CustomError
from backend.static.emails import EmailSender


class RecordMessageViewSet(viewsets.ModelViewSet):
    queryset = models.RecordMessage.objects.all()
    serializer_class = serializers.RecordMessageSerializer


class RecordMessageByRecordViewSet(APIView):
    def post(self, request, id):
        # request = self.request
        if 'message' not in request.data or request.data['message'] == '':
            raise CustomError(error_codes.ERROR__RECORD__MESSAGE__NO_MESSAGE_PROVIDED)
        message = request.data['message']

        try:
            record = models.Record.objects.get(pk=id)
        except Exception as e:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__NOT_EXISTING)
        if not record.user_has_permission(request.user):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        record_message = models.RecordMessage(sender=request.user, message=message, record=record)
        record_message.save()

        EmailSender.send_record_new_message_notification_email(record)
        return Response(serializers.RecordMessageSerializer(record_message).data)

    def get(self, request, id):
        pass
