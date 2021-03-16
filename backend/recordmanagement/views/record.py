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
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.response import Response
from backend.api.errors import CustomError
from backend.api.models import UserProfile
from backend.recordmanagement import models, serializers
from backend.static import error_codes, permissions


class RecordsListViewSet(viewsets.ViewSet):
    def list(self, request):
        """

        :param request:
        :return:
        """
        parts = request.query_params.get("search", "").split(" ")
        user = request.user

        if user.is_superuser:
            entries = models.Record.objects.all()
            for part in parts:
                consultants = UserProfile.objects.filter(name__icontains=part)
                entries = entries.filter(
                    Q(tagged__name__icontains=part)
                    | Q(note__icontains=part)
                    | Q(working_on_record__in=consultants)
                    | Q(record_token__icontains=part)
                ).distinct()
            serializer = serializers.RecordFullDetailSerializer(entries, many=True)
            return Response(serializer.data)

        if not user.has_permission(
            permissions.PERMISSION_VIEW_RECORDS_RLC, for_rlc=user.rlc
        ) and not user.has_permission(
            permissions.PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC, for_rlc=user.rlc
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        # entries = models.Record.objects.filter(from_rlc=user.rlc)
        entries = models.Record.objects.filter_by_rlc(user.rlc)
        for part in parts:
            consultants = UserProfile.objects.filter(name__icontains=part)
            entries = entries.filter(
                Q(tagged__name__icontains=part)
                | Q(note__icontains=part)
                | Q(working_on_record__in=consultants)
                | Q(record_token__icontains=part)
            ).distinct()

        records = []
        if user.has_permission(
            permissions.PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC, for_rlc=user.rlc
        ):
            queryset = entries
            serializer = serializers.RecordFullDetailSerializer(queryset, many=True)
            records += serializer.data
        else:
            queryset = entries.get_full_access_records(user).distinct()
            serializer = serializers.RecordFullDetailSerializer(queryset, many=True)
            records += serializer.data

            queryset = entries.get_no_access_records(user)
            serializer = serializers.RecordNoDetailSerializer(queryset, many=True)
            records += serializer.data
        return Response(records)

    def create(self, request):
        """outdated"""
        rlc = request.user.rlc
        record = models.Record(
            client_id=request.data["client"],
            first_contact_date=request.data["first_contact_date"],
            last_contact_date=request.data["last_contact_date"],
            record_token=request.data["record_token"],
            note=request.data["note"],
            creator_id=request.user.id,
            from_rlc_id=rlc.id,
        )
        record.save()
        for tag_id in request.data["tagged"]:
            record.tagged.add(models.RecordTag.objects.get(pk=tag_id))
        for user_id in request.data["working_on_record"]:
            record.working_on_record.add(UserProfile.objects.get(pk=user_id))
        record.save()
        return Response(serializers.RecordFullDetailSerializer(record).data)

    def retrieve(self, request, pk=None):
        # TODO: deprecated?
        try:
            record = models.Record.objects.get(pk=pk)
        except Exception as e:
            raise CustomError(error_codes.ERROR__RECORD__DOCUMENT__NOT_FOUND)

        if request.user.rlc != record.from_rlc and not request.user.is_superuser:
            raise CustomError(error_codes.ERROR__RECORD__RETRIEVE_RECORD__WRONG_RLC)
        if record.user_has_permission(request.user):
            serializer = serializers.RecordFullDetailSerializer(record)
        else:
            serializer = serializers.RecordNoDetailSerializer(record)
        return Response(serializer.data)
