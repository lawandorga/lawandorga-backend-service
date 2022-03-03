from apps.internal.models import Article, InternalUser, IndexPage, RoadmapItem, ImprintPage, TomsPage, HelpPage
from django.contrib import admin
from solo.admin import SingletonModelAdmin


class InternalUserAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']


admin.site.register(InternalUser, InternalUserAdmin)
admin.site.register(IndexPage, SingletonModelAdmin)
admin.site.register(ImprintPage, SingletonModelAdmin)
admin.site.register(TomsPage, SingletonModelAdmin)
admin.site.register(HelpPage, SingletonModelAdmin)
admin.site.register(RoadmapItem)
admin.site.register(Article)
