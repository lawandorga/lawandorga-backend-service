# Generated by Django 2.2.8 on 2020-01-04 12:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_auto_20191128_1714"),
    ]

    operations = [
        migrations.CreateModel(
            name="EncryptionKeys",
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
                ("private_key", models.BinaryField()),
                ("private_key_encrypted", models.BooleanField(default=False)),
                ("public_key", models.BinaryField()),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="encryption_keys",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]