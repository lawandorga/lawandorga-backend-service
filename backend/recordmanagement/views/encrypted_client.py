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

from backend.recordmanagement import serializers
from backend.recordmanagement.models.encrypted_client import EncryptedClient
from backend.recordmanagement.models.origin_country import OriginCountry
from backend.static.middleware import get_private_key_from_request


class EncryptedClientsViewSet(viewsets.ModelViewSet):
    queryset = EncryptedClient.objects.all()
    serializer_class = serializers.EncryptedClientSerializer

    def perform_create(self, serializer):
        country = OriginCountry.objects.get(id=self.request.data["origin_country"])
        serializer.save(origin_country=country)


class GetEncryptedClientsFromBirthday(APIView):
    def post(self, request):
        # TODO validate birthday
        users_private_key = get_private_key_from_request(request)
        rlcs_private_key = request.user.get_rlcs_private_key(users_private_key)
        birthday = request.data["birthday"]
        clients = EncryptedClient.objects.filter(
            birthday=request.data["birthday"], from_rlc=request.user.rlc
        )
        return Response(
            serializers.EncryptedClientSerializer(
                clients, many=True
            ).get_decrypted_data(rlcs_private_key)
        )
