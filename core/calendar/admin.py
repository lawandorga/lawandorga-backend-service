from django.contrib import admin

from .models import (
    CalendarEvent,
    CalendarEventAttachment,
    CalendarEventOccurrenceOverride,
    CalendarEventReminder,
    CalendarEventShare,
    CalendarNotification,
)

admin.site.register(CalendarEvent)
admin.site.register(CalendarEventAttachment)
admin.site.register(CalendarEventOccurrenceOverride)
admin.site.register(CalendarEventReminder)
admin.site.register(CalendarEventShare)
admin.site.register(CalendarNotification)
