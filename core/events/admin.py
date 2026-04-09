from django.contrib import admin

from .models import (
    CalendarEvent,
    CalendarEventAttachment,
    CalendarEventGuest,
    EventsEvent,
)

admin.site.register(EventsEvent)
admin.site.register(CalendarEvent)
admin.site.register(CalendarEventAttachment)
admin.site.register(CalendarEventGuest)
