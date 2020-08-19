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

from django.db.models import QuerySet


class QuerysetDifference:
    def __init__(self, org_queryset: QuerySet):
        self.items = list(org_queryset)
        self.exclude_ids = [item.id for item in org_queryset]

    def get_new_items(self, new_queryset: QuerySet) -> []:
        return list(self.get_new_queryset(new_queryset))

    def get_new_queryset(self, new_queryset: QuerySet) -> QuerySet:
        return new_queryset.exclude(id__in=self.exclude_ids)
