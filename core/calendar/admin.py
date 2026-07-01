from django.contrib import admin

from .models import (
    CalendarEvent,
    CalendarEventAttachment,
    CalendarEventShare,
)

admin.site.register(CalendarEvent)
admin.site.register(CalendarEventAttachment)
admin.site.register(CalendarEventShare)
