from core.data_sheets.use_cases.templates import (
    create_field,
    create_template,
    delete_field,
    delete_template,
    update_field,
    update_template,
)

COMMANDS = {
    "data_sheets/create_template": create_template,
    "data_sheets/update_template": update_template,
    "data_sheets/delete_template": delete_template,
    "data_sheets/create_field": create_field,
    "data_sheets/update_field": update_field,
    "data_sheets/delete_field": delete_field,
}
