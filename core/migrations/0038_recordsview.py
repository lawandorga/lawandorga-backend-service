# Generated by Django 4.1.7 on 2023-03-26 18:54

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0037_alter_recordsrecord_folder_uuid"),
    ]

    operations = [
        migrations.CreateModel(
            name="RecordsView",
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
                ("name", models.CharField(max_length=200)),
                ("columns", models.JSONField()),
                (
                    "uuid",
                    models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="records_views",
                        to="core.rlcuser",
                    ),
                ),
            ],
            options={
                "verbose_name": "RecordsView",
                "verbose_name_plural": "RecordsViews",
            },
        ),
    ]
