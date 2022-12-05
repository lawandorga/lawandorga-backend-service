from django.contrib import admin

from core.mail.models import MailAccount, MailAddress, MailDomain, MailOrg, MailUser
from core.mail.models.admin import MailAdmin
from core.mail.models.group import MailGroup

admin.site.register(MailUser)
admin.site.register(MailDomain)
admin.site.register(MailAddress)
admin.site.register(MailAccount)
admin.site.register(MailGroup)
admin.site.register(MailAdmin)
admin.site.register(MailOrg)
