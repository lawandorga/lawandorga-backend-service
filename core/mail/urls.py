from django.urls import include, path

from core.mail import api

urlpatterns = [
    path("domains/", include(api.domain_router.urls)),
    path("users/", include(api.user_router.urls)),
    path("query/", include(api.query_router.urls)),
]
