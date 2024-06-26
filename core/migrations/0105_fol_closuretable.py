# Generated by Django 5.0.2 on 2024-04-28 18:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0104_rename_foldersfolder_fol_folder_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="FOL_ClosureTable",
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
                    "child",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="parent_connections",
                        to="core.fol_folder",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children_connections",
                        to="core.fol_folder",
                    ),
                ),
            ],
            options={
                "verbose_name": "FOL_ClosureTable",
                "verbose_name_plural": "FOL_ClosureTables",
                "ordering": ["parent", "child"],
                "unique_together": {("parent", "child")},
            },
        ),
    ]
