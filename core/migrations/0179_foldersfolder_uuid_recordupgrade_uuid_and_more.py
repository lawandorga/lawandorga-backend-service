# Generated by Django 4.1.3 on 2022-12-05 12:32

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0178_rename_slug_rlcuser_uuid"),
    ]

    operations = [
        migrations.AddField(
            model_name="foldersfolder",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AddField(
            model_name="recordupgrade",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name="foldersfolder",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="recordupgrade",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
