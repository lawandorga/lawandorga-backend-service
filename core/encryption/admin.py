from django.contrib import admin

from core.encryption.models import GroupKey, Keyring, ObjectKey

admin.site.register(Keyring)
admin.site.register(ObjectKey)
admin.site.register(GroupKey)
