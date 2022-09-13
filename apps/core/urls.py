from django.urls import include, path

from apps.core.auth.urls import urlpatterns as auth_urlpatterns
from apps.core.collab.urls import router as collab_router
from apps.core.files.urls import router as files_router
from apps.core.internal.urls import router as internal_router
from apps.core.records.urls import router as records_router
from apps.core.rlc.urls import router as rlc_router
from apps.core.statistic.urls import router as statistics_router


urlpatterns = [
    *auth_urlpatterns,
    path("", include(rlc_router.urls)),
    path("", include(statistics_router.urls)),
    path("", include(internal_router.urls)),
    path("collab/", include(collab_router.urls)),
    path("files/", include(files_router.urls)),
    path("records/", include(records_router.urls)),
]
