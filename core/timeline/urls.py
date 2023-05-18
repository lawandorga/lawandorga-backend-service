from django.urls import include, path

from core.timeline.api import query_router, timeline_router

urlpatterns = [
    path("query/", include(query_router.urls)),
    path("timeline/", include(timeline_router.urls)),
]
