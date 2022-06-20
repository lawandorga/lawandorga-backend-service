# Generated by Django 3.2.12 on 2022-04-01 09:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0095_rename_statisticsuser_statisticuser"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="statisticuser",
            options={
                "ordering": ["user__name"],
                "verbose_name": "StatisticUser",
                "verbose_name_plural": "StatisticUsers",
            },
        ),
        migrations.AlterField(
            model_name="statisticuser",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="statistic_user",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
