# Generated by Django 5.1.7 on 2025-03-18 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0136_alter_group_org"),
    ]

    operations = [
        migrations.AddField(
            model_name="note",
            name="order",
            field=models.IntegerField(default=0),
        ),
    ]
