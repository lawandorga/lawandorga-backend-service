# Generated by Django 3.2.11 on 2022-02-10 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0083_auto_20220210_2012"),
    ]

    operations = [
        migrations.AddField(
            model_name="permission",
            name="description",
            field=models.TextField(blank=True),
        ),
    ]
