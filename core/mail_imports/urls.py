from django.urls import include, path

from core.mail_imports import api

urlpatterns = [
    path("query/", include(api.query_router.urls)),
]
