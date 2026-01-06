from typing import Union

from django.urls import URLPattern, URLResolver, include, path

from . import api

urlpatterns: list[Union[URLPattern, URLResolver]] = [
    path("", include(api.events_router.urls)),
    path("ics/<uuid:calendar_uuid>.ics", api.api_get_ics_calendar),
    path("ics_url/", include(api.events_ics_router.urls)),
]
