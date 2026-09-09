import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0172_calendar_recurrence"),
    ]

    operations = [
        migrations.CreateModel(
            name="CalendarLink",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("event_types", models.JSONField(default=list)),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "org_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="calendar_links",
                        to="core.orguser",
                    ),
                ),
            ],
            options={"verbose_name": "EVT_CalendarLink", "ordering": ["-created"]},
        ),
    ]
