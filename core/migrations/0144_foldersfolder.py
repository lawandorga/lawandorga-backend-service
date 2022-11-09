# Generated by Django 4.1.2 on 2022-11-08 12:51

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0143_alter_legalrequirementuser_unique_together"),
    ]

    operations = [
        migrations.CreateModel(
            name="FoldersFolder",
            fields=[
                ("parent", models.UUIDField(null=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("name", models.CharField(max_length=1000)),
                ("org_pk", models.IntegerField()),
                ("keys", models.JSONField()),
                ("upgrades", models.JSONField()),
            ],
            options={
                "verbose_name": "FoldersFolder",
                "verbose_name_plural": "FoldersFolders",
            },
        ),
    ]
