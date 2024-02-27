# This file adds the migration for the mail import

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    This class adds the mail import
    """

    dependencies = [
        ("core", "0092_remove_encryptedrecordmessage_message_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="MailImport",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
                ),
                ("sender", models.CharField(max_length=255)),
                ("bcc", models.CharField(blank=True, max_length=255)),
                ("subject", models.CharField(blank=True, max_length=255)),
                ("content", models.TextField(blank=True, max_length=255)),
                ("sending_datetime", models.DateTimeField(auto_now_add=True)),
                ("is_read", models.BooleanField(default=False)),
            ],
        ),
    ]
