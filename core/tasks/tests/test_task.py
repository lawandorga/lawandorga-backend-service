import pytest
from django.test import Client

from core.tasks.models.task import Task
from core.tasks.use_cases.task import create_task, delete_task, update_task
from core.tests.test_helpers import create_raw_org, create_raw_org_user


def test_create_task_with_single_assignee(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, save=True)
    assignee = create_raw_org_user(
        org=org, email="assignee@test.de", name="Assignee", save=True
    )

    create_task(creator, assignee_ids=[assignee.pk], title="Test Task")

    task = Task.objects.get()
    assert task is not None
    assert task.title == "Test Task"
    assert task.creator == creator
    assert list(task.assignees.all()) == [assignee]


def test_create_task_with_multiple_assignees(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, save=True)
    assignee1 = create_raw_org_user(
        org=org, email="assignee@test.de", name="Assignee", save=True
    )
    assignee2 = create_raw_org_user(
        org=org, email="assignee2@test.de", name="Assignee 2", save=True
    )

    create_task(
        creator, assignee_ids=[assignee1.pk, assignee2.pk], title="Multi Assignee Task"
    )

    task = Task.objects.get()
    assert task is not None
    assert task.title == "Multi Assignee Task"
    assert set(task.assignees.values_list("pk", flat=True)) == {
        assignee1.pk,
        assignee2.pk,
    }


def test_update_task_as_creator(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, save=True)
    assignee = create_raw_org_user(
        org=org, email="assignee@test.de", name="Assignee", save=True
    )

    create_task(creator, assignee_ids=[assignee.pk], title="Original")

    task = Task.objects.get()
    update_task(creator, task_id=task.uuid, title="Updated")

    task.refresh_from_db()
    assert task.title == "Updated"


def test_update_task_as_assignee(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, save=True)
    assignee = create_raw_org_user(
        org=org, email="assignee@test.de", name="Assignee", save=True
    )

    create_task(creator, assignee_ids=[assignee.pk], title="Original")

    task = Task.objects.get()
    update_task(assignee, task_id=task.uuid, title="Updated by assignee")

    task.refresh_from_db()
    assert task.title == "Updated by assignee"


def test_update_task_change_assignees(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, save=True)
    assignee1 = create_raw_org_user(
        org=org, email="assignee@test.de", name="Assignee", save=True
    )
    assignee2 = create_raw_org_user(
        org=org, email="assignee2@test.de", name="Assignee 2", save=True
    )

    create_task(creator, assignee_ids=[assignee1.pk], title="Task")

    task = Task.objects.get()
    update_task(creator, task_id=task.uuid, assignee_ids=[assignee1.pk, assignee2.pk])

    task.refresh_from_db()
    assert set(task.assignees.values_list("pk", flat=True)) == {
        assignee1.pk,
        assignee2.pk,
    }


def test_update_task_unauthorized(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, save=True)
    assignee = create_raw_org_user(
        org=org, email="assignee@test.de", name="Assignee", save=True
    )
    other = create_raw_org_user(org=org, email="other@test.de", name="Other", save=True)

    create_task(creator, assignee_ids=[assignee.pk], title="Task")

    task = Task.objects.get()
    with pytest.raises(PermissionError):
        update_task(other, task_id=task.uuid, title="Hacked")


def test_update_task_progress(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, save=True)
    assignee = create_raw_org_user(
        org=org, email="assignee@test.de", name="Assignee", save=True
    )

    create_task(creator, assignee_ids=[assignee.pk], title="Progress Task")

    task = Task.objects.get()
    assert task.progress == 0
    assert task.is_done is False

    update_task(creator, task_id=task.uuid, progress=50)
    task.refresh_from_db()
    assert task.progress == 50
    assert task.is_done is False

    update_task(creator, task_id=task.uuid, progress=100)
    task.refresh_from_db()
    assert task.progress == 100
    assert task.is_done is True


def test_update_task_priority(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, save=True)
    assignee = create_raw_org_user(
        org=org, email="assignee@test.de", name="Assignee", save=True
    )

    create_task(creator, assignee_ids=[assignee.pk], title="Priority Task")

    task = Task.objects.get()
    assert task.priority == "medium"

    update_task(creator, task_id=task.uuid, priority="urgent")
    task.refresh_from_db()
    assert task.priority == "urgent"


def test_delete_task(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, save=True)
    assignee = create_raw_org_user(
        org=org, email="assignee@test.de", name="Assignee", save=True
    )

    create_task(creator, assignee_ids=[assignee.pk], title="To Delete")

    task = Task.objects.get()
    delete_task(creator, task_uuid=task.uuid)

    assert Task.objects.count() == 0


def test_task_assignee_ids_and_names(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, save=True)
    assignee = create_raw_org_user(
        org=org, email="assignee@test.de", name="Assignee", save=True
    )

    create_task(creator, assignee_ids=[assignee.pk], title="Props Test")

    task = Task.objects.get()
    assert task.assignee_ids == [assignee.pk]
    assert task.assignee_names == [assignee.name]


def test_query_tasks(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, save=True)
    assignee = create_raw_org_user(
        org=org, email="assignee@test.de", name="Assignee", save=True
    )

    create_task(creator, assignee_ids=[assignee.pk], title="Assigned Task")
    create_task(creator, assignee_ids=[creator.pk], title="Self Task")

    client = Client()
    client.login(**getattr(assignee, "login_data"))
    response = client.get("/api/tasks/query/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Assigned Task"
    assert isinstance(data[0]["assignee_ids"], list)
    assert isinstance(data[0]["assignee_names"], list)
    assert "progress" in data[0]
    assert "priority" in data[0]
    assert "is_done" in data[0]
