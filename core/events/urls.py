from django.urls import include, path

from . import api

urlpatterns = [
    path("events/", include(api.events_router.urls)),
    path("events/ics/<uuid:calendar_uuid>.ics", api.get_ics_calendar),
]
