from django.contrib import admin

from messagebus.models import Message

admin.site.register(Message)
