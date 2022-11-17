from django.contrib import admin

from core.mail.models import MailAlias, MailDomain, MailUser

admin.site.register(MailUser)
admin.site.register(MailDomain)
admin.site.register(MailAlias)
