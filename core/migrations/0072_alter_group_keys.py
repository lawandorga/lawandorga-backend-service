# Generated by Django 4.2.5 on 2023-10-31 15:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0071_group_keys"),
    ]

    operations = [
        migrations.AlterField(
            model_name="group",
            name="keys",
            field=models.JSONField(default=list),
        ),
    ]