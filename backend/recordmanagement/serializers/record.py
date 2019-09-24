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


from rest_framework import serializers
from backend.recordmanagement.models import Record
from backend.api.serializers.user import UserProfileNameSerializer
from .record_tag import RecordTagNameSerializer


class RecordFullDetailSerializer(serializers.ModelSerializer):
    tagged = RecordTagNameSerializer(many=True, read_only=True)
    working_on_record = UserProfileNameSerializer(many=True, read_only=True)
    record_messages = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Record
        fields = '__all__'
        extra_kwargs = {
            'creator': {
                'read_only': True
            }
        }
    # TODO: create Record, validate Data?


class RecordNoDetailSerializer(serializers.ModelSerializer):
    tagged = RecordTagNameSerializer(many=True, read_only=True)
    working_on_record = UserProfileNameSerializer(many=True, read_only=True)
    state = serializers.CharField()

    class Meta:
        model = Record
        fields = ('id', 'last_contact_date', 'state', 'official_note',
                  'record_token', 'working_on_record', 'tagged')
# TODO: anonymized records?? old records, but well researched


class RecordTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ('id', 'record_token')
