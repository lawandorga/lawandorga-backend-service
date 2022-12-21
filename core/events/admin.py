from django.contrib import admin

from .models import Event
from .models import Attendance

admin.site.register(Event)
admin.site.register(Attendance)
