# Generated by Django 3.2.9 on 2021-11-24 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recordmanagement", "0060_auto_20211122_1658"),
    ]

    operations = [
        migrations.AddField(
            model_name="questionnairefield",
            name="ordering",
            field=models.IntegerField(default=0),
        ),
    ]
