from django.contrib import admin

from core.tasks.models.task import Task

admin.site.register(Task)
