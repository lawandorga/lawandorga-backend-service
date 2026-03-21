from django.db import migrations


def migrate_is_done_to_progress(apps, schema_editor):
    Task = apps.get_model("core", "Task")
    Task.objects.filter(is_done=True).update(progress=100)
    Task.objects.filter(is_done=False).update(progress=0)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0154_task_multiple_assignees"),
    ]

    operations = [
        migrations.RunPython(migrate_is_done_to_progress, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="task",
            name="is_done",
        ),
    ]
