# Generated by Django 4.1.3 on 2022-12-15 10:17

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("stream_name", models.CharField(max_length=1000)),
                ("action", models.SlugField(max_length=200)),
                ("position", models.IntegerField()),
                ("data", models.JSONField()),
                ("metadata", models.JSONField()),
                ("time", models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                "verbose_name": "Message",
                "verbose_name_plural": "Messages",
                "unique_together": {("position", "stream_name")},
            },
        ),
    ]
