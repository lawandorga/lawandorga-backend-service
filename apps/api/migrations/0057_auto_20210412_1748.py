# Generated by Django 3.1.6 on 2021-04-12 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0056_loggedpath"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="haspermission",
            name="permission_for_group",
        ),
        migrations.RemoveField(
            model_name="haspermission",
            name="permission_for_rlc",
        ),
        migrations.RemoveField(
            model_name="haspermission",
            name="permission_for_user",
        ),
    ]
