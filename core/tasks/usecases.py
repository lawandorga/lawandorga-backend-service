from core.tasks.use_cases.task import (
    create_task,
    delete_task,
    update_task,
)

USECASES = {
    "tasks/create_task": create_task,
    "tasks/update_task": update_task,
    "tasks/delete_task": delete_task,
}
