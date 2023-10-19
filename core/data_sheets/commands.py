from core.data_sheets.use_cases.entry import (
    create_entry,
    create_file_entry,
    delete_entry,
    update_entry,
)
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
    "data_sheets/create_entry": create_entry,
    "data_sheets/update_entry": update_entry,
    "data_sheets/create_file_entry": create_file_entry,
    "data_sheets/delete_entry": delete_entry,
}
