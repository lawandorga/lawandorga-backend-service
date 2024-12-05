from django.urls import include, path

from core.todos.api.query import router as query_router

urlpatterns = [
    path("", include(query_router.urls)),
]
