# Generated by Django 4.1.4 on 2022-12-20 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_record_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="foldersfolder",
            options={
                "ordering": ["name"],
                "verbose_name": "FoldersFolder",
                "verbose_name_plural": "FoldersFolders",
            },
        ),
    ]
