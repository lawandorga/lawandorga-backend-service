# Generated by Django 3.2.15 on 2022-08-15 11:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0110_auto_20220815_1343'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UsersRlcKeys',
            new_name='OrgEncryption',
        ),
    ]
