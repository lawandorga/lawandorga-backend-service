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
from typing import Any

from rest_framework import serializers

from backend.collab.models import CollabDocument, UserProfile


class CollabDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollabDocument
        fields = "__all__"


class CollabDocumentListSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = CollabDocument
        fields = (
            "pk",
            "name",
            "created",
            "creator",
            "last_edited",
            "last_editor",
            "children",
        )

    def get_children(self, instance):
        children = instance.child_pages.all().order_by("name")
        return CollabDocumentListSerializer(children, many=True).data


class CollabDocumentRecursiveSerializer(serializers.ModelSerializer):
    child_pages = serializers.SerializerMethodField("get_child_pages")

    def __init__(self, user: UserProfile, **kwargs: Any):
        super().__init__(**kwargs)
        self.user = user

    def get_child_pages(self, document: CollabDocument):
        queryset = CollabDocument.objects.filter(parent=document)
        # user.has_permission -> read all /write all /manage
        # if has -> see all

        # permission for collab documents check

        serializer = CollabDocumentRecursiveSerializer(
            instance=queryset, many=True, context=self.context, user=self.user
        )
        return serializer.data

    class Meta:
        model = CollabDocument
        fields = "__all__"
