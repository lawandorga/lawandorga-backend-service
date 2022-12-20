from django.urls import path, include

from core.files_new import api

urlpatterns = [
    path("", include(api.files_router.urls)),
]
