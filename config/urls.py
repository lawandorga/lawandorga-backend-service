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
from backend.recordmanagement import urls as record_urls
from django.views.generic import TemplateView
from django.contrib import admin
from backend.files import urls as file_urls
from backend.api import urls as api_urls
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
    path("api/records/", include(record_urls)),
    path("api/files/", include(file_urls)),
    path("prometheus/", include("django_prometheus.urls")),
    path("", TemplateView.as_view(template_name="index.html")),
]
