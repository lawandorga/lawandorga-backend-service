# Generated by Django 4.1.7 on 2023-03-28 11:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0045_alter_recordsview_options"),
    ]

    operations = [
        migrations.RenameField(
            model_name="foldersfolder",
            old_name="name_change_disabled",
            new_name="restricted",
        ),
    ]
