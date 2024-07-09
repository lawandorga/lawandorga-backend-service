from django.contrib import admin

from core.collab.models.footer import Footer
from core.collab.models.letterhead import Letterhead

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
admin.site.register(Letterhead)
admin.site.register(Footer)
