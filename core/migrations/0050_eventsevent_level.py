# Generated by Django 4.1.7 on 2023-04-23 19:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0049_rename_event_eventsevent"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventsevent",
            name="level",
            field=models.CharField(
                choices=[
                    ("ORG", "Organization"),
                    ("META", "Meta"),
                    ("GLOBAL", "Global"),
                ],
                default="ORG",
                max_length=200,
            ),
        ),
    ]
