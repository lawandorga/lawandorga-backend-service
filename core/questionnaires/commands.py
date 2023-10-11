from core.questionnaires.use_cases.questionnaire import (
    delete_a_questionnaire,
    publish_a_questionnaire,
    submit_answers,
)
from core.questionnaires.use_cases.template import (
    add_file,
    create_question,
    delete_file,
    delete_question,
    update_question,
)

COMMANDS = {
    "questionnaires/publish_questionnaire": publish_a_questionnaire,
    "questionnaires/create_question": create_question,
    "questionnaires/update_question": update_question,
    "questionnaires/delete_question": delete_question,
    "questionnaires/add_file": add_file,
    "questionnaires/delete_file": delete_file,
    "questionnaires/delete_questionnaire": delete_a_questionnaire,
    "questionnaires/submit_answers": submit_answers,
}
