from django.urls import include, path

from . import api

urlpatterns = [
    path("", include(api.events_router.urls)),
    path("ics/<uuid:calendar_uuid>.ics", api.get_ics_calendar),
    path("ics_url/", include(api.events_ics_router.urls)),
]
