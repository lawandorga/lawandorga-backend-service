from core.data_sheets.commands import COMMANDS as DATA_SHEET_COMMANDS
from core.folders.commands import COMMANDS as FOLDER_COMMANDS
from core.questionnaires.commands import COMMANDS as QUESTIONNAIRE_COMMANDS
from core.rlc.commands import COMMANDS as ORG_COMMANDS
from core.timeline.commands import COMMANDS as TIMELINE_USECASES

USECASES = {}
USECASES.update(TIMELINE_USECASES)
USECASES.update(QUESTIONNAIRE_COMMANDS)
USECASES.update(DATA_SHEET_COMMANDS)
USECASES.update(ORG_COMMANDS)
USECASES.update(FOLDER_COMMANDS)
