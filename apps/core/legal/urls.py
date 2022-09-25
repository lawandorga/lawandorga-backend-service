from django.urls import include, path

from . import api

urlpatterns = [
    path("legal_requirements/", include(api.legal_requirement_router.urls)),
]
