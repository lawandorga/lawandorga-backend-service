# Generated by Django 3.1.7 on 2021-03-24 20:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0005_auto_20210324_2139"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="folderpermission",
            options={
                "verbose_name": "FolderPermission",
                "verbose_name_plural": "FolderPermissions",
            },
        ),
    ]