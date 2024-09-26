from django.contrib import admin

from core.mail_imports.models.mail_import import MailAttachment, MailImport

admin.site.register(MailImport)
admin.site.register(MailAttachment)
