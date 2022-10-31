from django.contrib import admin

from core.mail.models import Alias, Domain, MailUser

admin.site.register(MailUser)
admin.site.register(Domain)
admin.site.register(Alias)
