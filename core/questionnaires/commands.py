from core.questionnaires.use_cases.template import (
    add_file,
    create_question,
    delete_file,
    delete_question,
    update_question,
)

COMMANDS = {
    "questionnaires/create_question": create_question,
    "questionnaires/update_question": update_question,
    "questionnaires/delete_question": delete_question,
    "questionnaires/add_file": add_file,
    "questionnaires/delete_file": delete_file,
}
