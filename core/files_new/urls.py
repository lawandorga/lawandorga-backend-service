from django.urls import include, path

from core.files_new import api

urlpatterns = [
    path("query/", include(api.query_router.urls)),
]
