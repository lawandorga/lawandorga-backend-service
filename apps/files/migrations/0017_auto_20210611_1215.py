# Generated by Django 3.1.6 on 2021-06-11 10:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0016_auto_20210611_1212"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="file",
            options={
                "ordering": ["-exists", "-created"],
                "verbose_name": "File",
                "verbose_name_plural": "Files",
            },
        ),
    ]
