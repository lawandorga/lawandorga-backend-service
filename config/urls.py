from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView

from core import urls as api_urls
from core.auth.api.user import CustomLoginView


class EmailView(APIView):
    def get_permissions(self):
        return []

    def get(self, request, *args, **kwargs):
        send_mail(
            "Test Mail",
            "Test Body",
            settings.SERVER_EMAIL,
            [a[1] for a in settings.ADMINS],
            fail_silently=False,
        )
        return Response({"status": "email sent"})


handler400 = "config.handlers.handler400"
handler403 = "config.handlers.handler403"
handler404 = "config.handlers.handler404"
handler500 = "config.handlers.handler500"


urlpatterns = [
    path("error/", TemplateView.as_view(template_name="")),
    path("email/", EmailView.as_view()),
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
    path("login/", CustomLoginView.as_view()),
    path(
        "",
        TemplateView.as_view(
            template_name="index.html",
            extra_context={
                "RUNTIME": settings.RUNTIME,
                "SERVICE": settings.SERVICE,
                "IMAGE": settings.IMAGE,
            },
        ),
    ),
    path("tinymce/", include("tinymce.urls")),
    path("openid/", include("oidc_provider.urls", namespace="oidc_provider")),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
