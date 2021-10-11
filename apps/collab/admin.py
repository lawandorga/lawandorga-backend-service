from django.contrib import admin
from apps.collab.models import *

# Register your models here.
admin.site.register(CollabDocument)
admin.site.register(CollabPermission)
admin.site.register(EditingRoom)
admin.site.register(PermissionForCollabDocument)
admin.site.register(RecordDocument)
admin.site.register(TextDocument)
admin.site.register(TextDocumentVersion)
