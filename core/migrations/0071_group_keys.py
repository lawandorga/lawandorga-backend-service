# Generated by Django 4.2.5 on 2023-10-31 15:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0070_rename_recordencryptionnew_datasheetencryptionnew"),
    ]

    operations = [
        migrations.AddField(
            model_name="group",
            name="keys",
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
