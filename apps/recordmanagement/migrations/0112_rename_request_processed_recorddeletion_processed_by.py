# Generated by Django 3.2.10 on 2022-01-03 18:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "recordmanagement",
            "0111_rename_encryptedrecorddeletionrequest_recorddeletion",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="recorddeletion",
            old_name="request_processed",
            new_name="processed_by",
        ),
    ]
