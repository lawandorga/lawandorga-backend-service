# Generated by Django 4.1.6 on 2023-02-06 10:23

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0030_alter_legalrequirementuser_options"),
    ]

    operations = [
        migrations.RenameField(
            model_name="group",
            old_name="members",
            new_name="_members",
        ),
    ]
