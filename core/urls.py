from django.urls import include, path

from core.auth.urls import urlpatterns as auth_urlpatterns
from core.collab.urls import router as collab_router
from core.cronjobs import router as cronjobs_router
from core.events.urls import urlpatterns as events_urlpatterns
from core.files.urls import router as files_router
from core.folders.urls import urlpatterns as folders_urlpatterns
from core.internal.urls import router as internal_router
from core.legal.urls import urlpatterns as legal_urlpatterns
from core.records.urls import urlpatterns as records_urlpatterns
from core.rlc.urls import urlpatterns as org_urlpatterns
from core.statistics.urls import urlpatterns as statistics_urlpatterns

urlpatterns = [
    *auth_urlpatterns,
    *statistics_urlpatterns,
    path("folders/", include(folders_urlpatterns)),
    path("events/", include(events_urlpatterns)),
    path("legal/", include(legal_urlpatterns)),
    path("cronjobs/", include(cronjobs_router.urls)),
    path("", include(org_urlpatterns)),
    path("", include(internal_router.urls)),
    path("collab/", include(collab_router.urls)),
    path("files/", include(files_router.urls)),
    path("records/", include(records_urlpatterns)),
]
