from core.auth.usecases import USECASES as AUTH_USECASES
from core.collab.usecases import USECASES as COLLAB_USECASES
from core.data_sheets.commands import COMMANDS as DATA_SHEET_COMMANDS
from core.folders.commands import COMMANDS as FOLDER_COMMANDS
from core.legal.usecases import USECASES as LEGAL_USECASES
from core.questionnaires.commands import COMMANDS as QUESTIONNAIRE_COMMANDS
from core.rlc.commands import COMMANDS as ORG_COMMANDS
from core.timeline.commands import COMMANDS as TIMELINE_USECASES

USECASES = {}
USECASES.update(TIMELINE_USECASES)
USECASES.update(QUESTIONNAIRE_COMMANDS)
USECASES.update(DATA_SHEET_COMMANDS)
USECASES.update(ORG_COMMANDS)
USECASES.update(FOLDER_COMMANDS)
USECASES.update(COLLAB_USECASES)
USECASES.update(LEGAL_USECASES)
USECASES.update(AUTH_USECASES)
