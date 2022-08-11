from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core import urls as api_urls


class EmailView(APIView):
    def get_permissions(self):
        return []

    def get(self, request, *args, **kwargs):
        send_mail(
            "Test Mail",
            "Test Body",
            "no-reply@law-orga.de",
            [a[1] for a in settings.ADMINS],
            fail_silently=False,
        )
        return Response({"status": "email sent"})


urlpatterns = [
    path("error/", TemplateView.as_view(template_name="")),
    path("email/", EmailView.as_view()),
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
    path(
        "",
        TemplateView.as_view(
            template_name="index.html",
            extra_context={"RUNTIME": settings.RUNTIME, "PORT": settings.EMAIL_PORT},
        ),
    ),
    path("tinymce/", include("tinymce.urls")),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
