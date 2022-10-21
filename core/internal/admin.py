from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import Article, HelpPage, ImprintPage, IndexPage, RoadmapItem, TomsPage

admin.site.register(Article)
admin.site.register(HelpPage, SingletonModelAdmin)
admin.site.register(ImprintPage, SingletonModelAdmin)
admin.site.register(IndexPage, SingletonModelAdmin)
admin.site.register(RoadmapItem)
admin.site.register(TomsPage, SingletonModelAdmin)
