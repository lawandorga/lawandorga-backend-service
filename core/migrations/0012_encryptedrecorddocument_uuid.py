# Generated by Django 4.1.4 on 2022-12-20 18:07

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "core",
            "0009_encryptedrecorddocument_folder_uuid_squashed_0011_alter_encryptedrecorddocument_updated",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="encryptedrecorddocument",
            name="uuid",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, null=True),
        ),
    ]
