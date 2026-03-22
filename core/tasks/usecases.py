from core.tasks.use_cases.task import (
    add_comment,
    create_task,
    delete_task,
    update_task,
)

USECASES = {
    "tasks/create_task": create_task,
    "tasks/update_task": update_task,
    "tasks/add_comment": add_comment,
    "tasks/delete_task": delete_task,
}
