from core.auth.usecases import USECASES as AUTH_USECASES
from core.collab.usecases import USECASES as COLLAB_USECASES
from core.data_sheets.usecases import USECASES as DATA_SHEET_USECASES
from core.events.usecases import USECASES as EVENTS_USECASES
from core.files_new.usecases import USECASES as FILES_NEW_USECASES
from core.folders.usecases import USECASES as FOLDER_USECASES
from core.legal.usecases import USECASES as LEGAL_USECASES
from core.mail.usecases import USECASES as MAIL_USECASES
from core.mail_imports.usecases import USECASES as MAIL_IMPORTS_USECASES
from core.messages.usecases import USECASES as MESSAGES_USECASES
from core.org.usecases import USECASES as ORG_USECASES
from core.permissions.usecases import USECASES as PERMISSIONS_USECASES
from core.questionnaires.usecases import USECASES as QUESTIONNAIRE_USECASES
from core.records.usecases import USECASES as RECORDS_USECASES
from core.tasks.usecases import USECASES as TASKS_USECASES
from core.timeline.usecases import USECASES as TIMELINE_USECASES
from core.upload.usecases import USECASES as UPLOAD_USECASES

USECASES = {}
USECASES.update(TIMELINE_USECASES)
USECASES.update(QUESTIONNAIRE_USECASES)
USECASES.update(DATA_SHEET_USECASES)
USECASES.update(ORG_USECASES)
USECASES.update(FOLDER_USECASES)
USECASES.update(COLLAB_USECASES)
USECASES.update(LEGAL_USECASES)
USECASES.update(AUTH_USECASES)
USECASES.update(EVENTS_USECASES)
USECASES.update(FILES_NEW_USECASES)
USECASES.update(UPLOAD_USECASES)
USECASES.update(MAIL_USECASES)
USECASES.update(PERMISSIONS_USECASES)
USECASES.update(RECORDS_USECASES)
USECASES.update(MESSAGES_USECASES)
USECASES.update(MAIL_IMPORTS_USECASES)
USECASES.update(TASKS_USECASES)
