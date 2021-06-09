from solo.admin import SingletonModelAdmin

from backend.internal.models import Article, InternalUser, IndexPage
from django.contrib import admin


class InternalUserAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']


admin.site.register(InternalUser, InternalUserAdmin)
admin.site.register(Article)
admin.site.register(IndexPage, SingletonModelAdmin)
