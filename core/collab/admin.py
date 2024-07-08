from django.contrib import admin

from .models import (
    Collab,
    CollabDocument,
    CollabPermission,
    PermissionForCollabDocument,
    TextDocumentVersion,
)

admin.site.register(CollabDocument)
admin.site.register(CollabPermission)
admin.site.register(PermissionForCollabDocument)
admin.site.register(TextDocumentVersion)
admin.site.register(Collab)
