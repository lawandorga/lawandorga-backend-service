# Generated by Django 4.2.5 on 2023-09-22 10:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0059_timelinefollowup"),
    ]

    operations = [
        migrations.CreateModel(
            name="TimelineEvent",
            fields=[
                ("uuid", models.UUIDField(primary_key=True, serialize=False)),
                ("text_enc", models.JSONField(default=dict)),
                ("title_enc", models.JSONField(default=dict)),
                ("time", models.DateTimeField()),
                ("folder_uuid", models.UUIDField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "org",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="timeline_events",
                        to="core.org",
                    ),
                ),
            ],
        ),
    ]
