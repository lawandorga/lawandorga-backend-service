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


class RecordDocumentTagViewSet(viewsets.ModelViewSet):
    queryset = models.RecordDocumentTag.objects.all()
    serializer_class = serializers.RecordDocumentTagSerializer


class RecordDocumentTagByDocumentViewSet(APIView):
    def post(self, request, id):
        try:
            document = models.RecordDocument.objects.get(pk=id)
        except Exception as e:
            raise CustomError(error_codes.ERROR__RECORD__DOCUMENT__NOT_FOUND)
        if not document.record:
            raise CustomError(error_codes.ERROR__RECORD__DOCUMENT__NO_LINKED_RECORD)
        if not document.record.user_has_permission(request.user):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        if 'tag_ids' not in request.data:
            raise CustomError(error_codes.ERROR__RECORD__DOCUMENT__NO_TAG_PROVIDED)

        tags = []
        for tag in request.data['tag_ids']:
            try:
                real_tag = models.RecordDocumentTag.objects.get(pk=tag['id'])  # tag_ids
            except Exception as e:
                raise CustomError(error_codes.ERROR__RECORD__DOCUMENT__TAG_NOT_EXISTING)
            tags.append(real_tag)

        document.tagged.clear()
        for tag in tags:
            document.tagged.add(tag)
        document.save()
        serializer = serializers.RecordDocumentSerializer(document)
        return Response(serializer.data)
