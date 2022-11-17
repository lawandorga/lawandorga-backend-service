from django.contrib import admin

from core.mail.models import MailAddress, MailDomain, MailUser

admin.site.register(MailUser)
admin.site.register(MailDomain)
admin.site.register(MailAddress)
