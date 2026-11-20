from django.contrib import admin
from django.utils.html import format_html
from solo.admin import SingletonModelAdmin

from .models import (
    Article,
    FeatureArea,
    HelpPage,
    ImprintPage,
    IndexPage,
    RoadmapItem,
    TomsPage,
)


def image_preview(file, height: int = 120):
    if not file:
        return "-"
    return format_html(
        '<img src="{}" alt="" style="max-height: {}px; max-width: 100%; background: #EBEDF0; padding: 4px;">',
        file.url,
        height,
    )


@admin.register(FeatureArea)
class FeatureAreaAdmin(admin.ModelAdmin):
    list_display = ["title", "placement", "position", "is_published", "has_screenshot"]
    list_editable = ["position", "is_published"]
    list_filter = ["placement", "is_published"]
    search_fields = ["title"]
    readonly_fields = ["icon_preview", "screenshot_preview", "created", "updated"]
    fields = [
        "title",
        "description",
        "placement",
        "position",
        "is_published",
        "icon",
        "icon_preview",
        "screenshot",
        "screenshot_preview",
        "screenshot_alt",
        "screenshot_note",
        "created",
        "updated",
    ]

    @admin.display(boolean=True, description="Screenshot")
    def has_screenshot(self, obj: FeatureArea) -> bool:
        return bool(obj.screenshot)

    @admin.display(description="Icon preview")
    def icon_preview(self, obj: FeatureArea):
        return image_preview(obj.icon, 64)

    @admin.display(description="Screenshot preview")
    def screenshot_preview(self, obj: FeatureArea):
        return image_preview(obj.screenshot, 240)


@admin.register(RoadmapItem)
class RoadmapItemAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "position", "date", "is_published"]
    list_editable = ["position", "is_published"]
    list_filter = ["status", "is_published"]
    search_fields = ["title"]
    readonly_fields = ["icon_preview", "created", "updated"]
    fields = [
        "title",
        "status",
        "stage",
        "date",
        "position",
        "is_published",
        "description",
        "benefits",
        "status_note",
        "icon",
        "icon_preview",
        "created",
        "updated",
    ]

    @admin.display(description="Icon preview")
    def icon_preview(self, obj: RoadmapItem):
        return image_preview(obj.icon, 64)


admin.site.register(Article)
admin.site.register(HelpPage, SingletonModelAdmin)
admin.site.register(ImprintPage, SingletonModelAdmin)
admin.site.register(IndexPage, SingletonModelAdmin)
admin.site.register(TomsPage, SingletonModelAdmin)
