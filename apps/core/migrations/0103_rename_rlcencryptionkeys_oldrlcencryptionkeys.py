# Generated by Django 3.2.14 on 2022-07-27 18:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0102_auto_20220726_1744"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="RlcEncryptionKeys",
            new_name="OldRlcEncryptionKeys",
        ),
    ]