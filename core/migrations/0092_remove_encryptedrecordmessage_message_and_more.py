# Generated by Django 4.2.5 on 2024-02-19 18:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0091_alter_encryptedrecordmessage_folder_uuid"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="encryptedrecordmessage",
            name="message",
        ),
        migrations.RemoveField(
            model_name="encryptedrecordmessage",
            name="record",
        ),
        migrations.AlterField(
            model_name="encryptedrecordmessage",
            name="enc_message",
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name="encryptedrecordmessage",
            name="key",
            field=models.JSONField(),
        ),
    ]
