from django.contrib import admin

from core.encryption.models import GroupKey, Keyring

admin.site.register(Keyring)
admin.site.register(GroupKey)
