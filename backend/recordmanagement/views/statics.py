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
from rest_framework.views import APIView
from rest_framework.response import Response

from backend.api.serializers import UserProfileNameSerializer
from ..serializers import RecordTagNameSerializer, OriginCountryNameStateSerializer, RecordDocumentTagSerializer
from ..models import RecordTag, OriginCountry, Record, RecordDocumentTag, UserProfile


class StaticViewSet(APIView):
    def get(self, request):
        user = request.user

        if user.rlc is None:
            consultants = []
        else:
            consultants = UserProfileNameSerializer(user.rlc.get_consultants(), many=True).data

        record_tags = RecordTagNameSerializer(RecordTag.objects.all(), many=True).data
        countries = OriginCountryNameStateSerializer(OriginCountry.objects.all(), many=True).data
        document_tags = RecordDocumentTagSerializer(RecordDocumentTag.objects.all(), many=True).data

        states_for_records = Record.record_states_possible
        states_for_countries = OriginCountry.origin_country_states_possible

        return Response({
            'record_tags': record_tags,
            'consultants': consultants,
            'countries': countries,
            'record_states': states_for_records,
            'country_states': states_for_countries,
            'record_document_tags': document_tags
        })
