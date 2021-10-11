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


from rest_framework import serializers

from apps.collab.models import TextDocumentVersion

from apps.api.serializers import UserProfileNameSerializer
from apps.collab.serializers import TextDocumentSerializer


class TextDocumentVersionSerializer(serializers.ModelSerializer):
    content = serializers.CharField()

    class Meta:
        model = TextDocumentVersion
        fields = "__all__"


class TextDocumentVersionDetailSerializer(TextDocumentVersionSerializer):
    creator = UserProfileNameSerializer(many=False, read_only=True)
    document = TextDocumentSerializer(many=False, read_only=True)


class TextDocumentVersionListSerializer(serializers.ModelSerializer):
    document = TextDocumentSerializer(many=False, read_only=True)
    creator = UserProfileNameSerializer(many=False, read_only=True)

    class Meta:
        model = TextDocumentVersion
        fields = ("creator", "created", "document", "is_draft", "id")
