# Generated by Django 4.2.5 on 2023-12-18 20:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0085_alter_group_options_alter_meta_options_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="datasheet",
            name="old_client",
        ),
        migrations.DeleteModel(
            name="EncryptedClient",
        ),
    ]
