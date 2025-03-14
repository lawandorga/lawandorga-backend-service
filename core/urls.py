from django.urls import include, path

from core.auth.urls import api_urlpatterns as auth_api_urlpatterns
from core.auth.urls import view_urlpatterns as auth_view_urlpatterns
from core.command import django_command
from core.cronjobs import router as cronjobs_router
from core.data_sheets.urls import urlpatterns as data_sheets_urlpatterns
from core.events.urls import urlpatterns as events_urlpatterns
from core.files.urls import router as files_router
from core.files_new.urls import urlpatterns as files_new_urlpatterns
from core.folders.urls import urlpatterns as folders_urlpatterns
from core.internal.urls import urlpatterns as internal_urlpatterns
from core.legal.urls import urlpatterns as legal_urlpatterns
from core.mail.urls import urlpatterns as mail_urlpatterns
from core.messages.urls import urlpatterns as messages_urlpatterns
from core.org.urls import urlpatterns as org_urlpatterns
from core.questionnaires.urls import urlpatterns as questionnaires_urlpatterns
from core.records.urls import urlpatterns as records_urlpatterns
from core.statistics.urls import urlpatterns as statistics_urlpatterns
from core.upload.urls import urlpatterns as upload_urlpatterns

urlpatterns = [
    path("auth/", include(auth_view_urlpatterns)),
    path("api/command/", django_command),
    path("api/mail/", include(mail_urlpatterns)),
    path("api/statistics/", include(statistics_urlpatterns)),
    path("api/messages/", include(messages_urlpatterns)),
    path("api/auth/", include(auth_api_urlpatterns)),
    path("api/folders/", include(folders_urlpatterns)),
    path("api/events/", include(events_urlpatterns)),
    path("api/legal/", include(legal_urlpatterns)),
    path("api/cronjobs/", include(cronjobs_router.urls)),
    path("api/org/", include(org_urlpatterns)),
    path("api/internal/", include(internal_urlpatterns)),
    path("api/collab/", include("core.collab.urls")),
    path("api/files/", include(files_router.urls)),
    path("api/files/v2/", include(files_new_urlpatterns)),
    path("api/data_sheets/", include(data_sheets_urlpatterns)),
    path("api/records/", include(records_urlpatterns)),
    path("api/questionnaires/", include(questionnaires_urlpatterns)),
    path("api/uploads/", include(upload_urlpatterns)),
    path("api/timeline/", include("core.timeline.urls")),
    path("api/permissions/", include("core.permissions.urls")),
    path("api/mail_imports/", include("core.mail_imports.urls")),
    path("api/tasks/", include("core.tasks.urls")),
]
