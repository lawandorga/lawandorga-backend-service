from django.urls import include, path

from core.auth.urls import urlpatterns as auth_urlpatterns
from core.collab.urls import router as collab_router
from core.cronjobs import router as cronjobs_router
from core.events.urls import urlpatterns as events_urlpatterns
from core.files.urls import router as files_router
from core.files_new.urls import urlpatterns as files_new_urlpatterns
from core.folders.urls import urlpatterns as folders_urlpatterns
from core.internal.urls import router as internal_router
from core.legal.urls import urlpatterns as legal_urlpatterns
from core.mail.urls import urlpatterns as mail_urlpatterns
from core.messages.urls import urlpatterns as messages_urlpatterns
from core.records.urls import urlpatterns as records_urlpatterns
from core.rlc.urls import urlpatterns as org_urlpatterns
from core.statistics.urls import urlpatterns as statistics_urlpatterns

urlpatterns = [
    path("api/mail/", include(mail_urlpatterns)),
    path("api/", include(statistics_urlpatterns)),
    path("api/messages/", include(messages_urlpatterns)),
    path("", include(auth_urlpatterns)),
    path("api/folders/", include(folders_urlpatterns)),
    path("api/events/", include(events_urlpatterns)),
    path("api/legal/", include(legal_urlpatterns)),
    path("api/cronjobs/", include(cronjobs_router.urls)),
    path("api/", include(org_urlpatterns)),
    path("api/", include(internal_router.urls)),
    path("api/collab/", include(collab_router.urls)),
    path("api/files/", include(files_router.urls)),
    path("api/files/v2/", include(files_new_urlpatterns)),
    path("api/records/", include(records_urlpatterns)),
]
