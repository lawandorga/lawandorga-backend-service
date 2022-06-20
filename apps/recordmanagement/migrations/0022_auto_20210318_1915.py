# Generated by Django 3.0 on 2021-03-18 18:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0033_auto_20210318_1915"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recordmanagement", "0021_auto_20210316_1513"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="record",
            name="client",
        ),
        migrations.RemoveField(
            model_name="record",
            name="creator",
        ),
        migrations.RemoveField(
            model_name="record",
            name="from_rlc",
        ),
        migrations.RemoveField(
            model_name="record",
            name="tagged",
        ),
        migrations.RemoveField(
            model_name="record",
            name="working_on_record",
        ),
        migrations.RemoveField(
            model_name="recorddeletionrequest",
            name="record",
        ),
        migrations.RemoveField(
            model_name="recorddeletionrequest",
            name="request_from",
        ),
        migrations.RemoveField(
            model_name="recorddeletionrequest",
            name="request_processed",
        ),
        migrations.RemoveField(
            model_name="recorddocument",
            name="creator",
        ),
        migrations.RemoveField(
            model_name="recorddocument",
            name="record",
        ),
        migrations.RemoveField(
            model_name="recorddocument",
            name="tagged",
        ),
        migrations.RemoveField(
            model_name="recordmessage",
            name="record",
        ),
        migrations.RemoveField(
            model_name="recordmessage",
            name="sender",
        ),
        migrations.RemoveField(
            model_name="recordpermission",
            name="record",
        ),
        migrations.RemoveField(
            model_name="recordpermission",
            name="request_from",
        ),
        migrations.RemoveField(
            model_name="recordpermission",
            name="request_processed",
        ),
        migrations.AlterField(
            model_name="encryptedrecord",
            name="client",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="e_records",
                to="recordmanagement.EncryptedClient",
            ),
        ),
        migrations.AlterField(
            model_name="encryptedrecord",
            name="creator",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="encrypted_records",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="encryptedrecord",
            name="from_rlc",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="encrypted_records",
                to="api.Rlc",
            ),
        ),
        migrations.AlterField(
            model_name="encryptedrecord",
            name="tagged",
            field=models.ManyToManyField(
                related_name="e_tagged", to="recordmanagement.RecordTag"
            ),
        ),
        migrations.AlterField(
            model_name="encryptedrecord",
            name="working_on_record",
            field=models.ManyToManyField(
                related_name="working_on_e_record", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name="encryptedrecordmessage",
            name="record",
            field=models.ForeignKey(
                db_index=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="messages",
                to="recordmanagement.EncryptedRecord",
            ),
        ),
        migrations.DeleteModel(
            name="Client",
        ),
        migrations.DeleteModel(
            name="Record",
        ),
        migrations.DeleteModel(
            name="RecordDeletionRequest",
        ),
        migrations.DeleteModel(
            name="RecordDocument",
        ),
        migrations.DeleteModel(
            name="RecordMessage",
        ),
        migrations.DeleteModel(
            name="RecordPermission",
        ),
    ]
