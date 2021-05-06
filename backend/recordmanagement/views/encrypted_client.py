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
from backend.recordmanagement.models.encrypted_client import EncryptedClient
from backend.recordmanagement import serializers
from rest_framework import viewsets


class EncryptedClientViewSet(viewsets.ModelViewSet):
    queryset = EncryptedClient.objects.all()
    serializer_class = serializers.OldEncryptedClientSerializer

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return serializers.EncryptedClientSerializer
        return super().get_serializer_class()

    def get_object(self):
        self.instance = super().get_object()
        self.private_key_user = self.request.user.get_private_key(request=self.request)
        self.private_key_rlc = self.request.user.rlc.get_private_key(user=self.request.user,
                                                                     private_key_user=self.private_key_user)
        self.instance.decrypt(private_key_rlc=self.private_key_rlc)
        return self.instance

    def perform_update(self, serializer):
        for attr, value in serializer.validated_data.items():
            setattr(self.instance, attr, value)
        self.instance.encrypt(public_key_rlc=self.request.user.rlc.get_public_key())
        self.instance.save()
        self.instance.decrypt(private_key_rlc=self.private_key_rlc)

    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #
    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         # If 'prefetch_related' has been applied to a queryset, we need to
    #         # forcibly invalidate the prefetch cache on the instance.
    #         instance._prefetched_objects_cache = {}
    #
    #     return Response(serializer.data)
    #
    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     private_key_user = request.user.get_private_key(request=request)
    #     private_key_rlc = request.user.rlc.get_private_key(user=request.user, private_key_user=private_key_user)
    #     instance.decrypt(private_key_rlc=private_key_rlc)
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)
