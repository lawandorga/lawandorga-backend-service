from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from core.auth.models import RlcUser


def get_ics_calendar(request, pk: int):
    user = get_object_or_404(RlcUser, pk=pk)
    calendar = user.get_ics_calendar()
    return HttpResponse(calendar, content_type="text/calendar")
