from backend.internal.models import Article, InternalUser
from django.contrib import admin


class InternalUserAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']


admin.site.register(InternalUser, InternalUserAdmin)
admin.site.register(Article)
