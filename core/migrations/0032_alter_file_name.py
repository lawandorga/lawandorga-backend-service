# Generated by Django 4.1.6 on 2023-02-09 16:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0031_rename_members_group__members"),
    ]

    operations = [
        migrations.AlterField(
            model_name="file",
            name="name",
            field=models.CharField(max_length=1000),
        ),
    ]
