# Generated by Django 4.1.4 on 2022-12-22 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_rename_key_encryptedrecorddocument_location"),
    ]

    operations = [
        migrations.AddField(
            model_name="encryptedrecorddocument",
            name="key",
            field=models.JSONField(null=True),
        ),
    ]