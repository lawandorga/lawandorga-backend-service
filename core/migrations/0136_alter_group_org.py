# Generated by Django 5.1.7 on 2025-03-11 15:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0135_rename_from_rlc_group_org_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="group",
            name="org",
            field=models.ForeignKey(
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="groups",
                to="core.org",
            ),
        ),
    ]
