# Generated by Django 4.1.3 on 2022-11-17 15:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0164_alter_mailaccount_group_alter_mailaccount_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mailuser",
            name="relative_path",
        ),
    ]
