from django.urls import include, path

from . import api

urlpatterns = [
    path("ics/<uuid:calendar_uuid>.ics", api.api_get_ics_calendar_link),
    path("query/", include(api.query_router.urls)),
]
