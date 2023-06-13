from django.urls import include, path
from . import api

urlpatterns = [
    path("query/", include(api.query_router.urls))
]