import time

from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView, View

from core import urls as api_urls
from core.auth.views.user import CustomLoginView, CustomRedirectView


class EmailView(View):
    def get(self, request, *args, **kwargs):
        send_mail(
            "Test Mail",
            "Test Body",
            settings.SERVER_EMAIL,
            [a[1] for a in settings.ADMINS],
            fail_silently=False,
        )
        return JsonResponse({"status": "email sent"})


class TimeoutView(View):
    def get(self, request, *args, **kwargs):
        time.sleep(200)
        return JsonResponse({"status": "OK"})


handler400 = "config.handlers.handler400"
handler403 = "config.handlers.handler403"
handler404 = "config.handlers.handler404"
handler500 = "config.handlers.handler500"


urlpatterns = [
    path("error/", TemplateView.as_view(template_name="")),
    path("email/", EmailView.as_view()),
    path("timeout/", TimeoutView.as_view()),
    path("", include(api_urls)),
    path("admin/login/", RedirectView.as_view(pattern_name="login", query_string=True)),
    path("logout/", RedirectView.as_view(pattern_name="logout", query_string=True)),
    path("admin/", admin.site.urls),
    path("login/", CustomLoginView.as_view()),
    path("redirect/", CustomRedirectView.as_view(), name="redirect"),
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
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots.txt",
    ),
    path("tinymce/", include("tinymce.urls")),
    path("openid/", include("oidc_provider.urls", namespace="oidc_provider")),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
