from apps.collab.models import CollabDocument, CollabPermission, PermissionForCollabDocument, TextDocumentVersion
from django.contrib import admin

admin.site.register(CollabDocument)
admin.site.register(CollabPermission)
admin.site.register(PermissionForCollabDocument)
admin.site.register(TextDocumentVersion)
