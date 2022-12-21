from django.urls import include, path

from core.files_new import api

urlpatterns = [
    path("", include(api.files_router.urls)),
    path("query/", include(api.query_router.urls)),
]
