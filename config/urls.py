from apps.recordmanagement import urls as record_urls
from django.views.generic import TemplateView
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from apps.api import urls as api_urls


urlpatterns = [
    path('error/', TemplateView.as_view(template_name='')),
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
    path("api/records/", include(record_urls)),
    path("", TemplateView.as_view(template_name="index.html", extra_context={'RUNTIME': settings.RUNTIME})),
    path('tinymce/', include('tinymce.urls')),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
