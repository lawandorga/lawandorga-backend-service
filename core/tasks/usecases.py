from core.tasks.use_cases.task import create_task, delete_task, mark_tasks_as_done

USECASES = {
    "tasks/mark_tasks_as_done": mark_tasks_as_done,
    "tasks/create_task": create_task,
    "tasks/delete_task": delete_task,
}
