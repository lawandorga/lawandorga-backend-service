# Generated by Django 3.1.6 on 2021-06-11 10:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0015_auto_20210609_1134'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='file',
            options={'ordering': ['exists', 'created'], 'verbose_name': 'File', 'verbose_name_plural': 'Files'},
        ),
        migrations.RemoveField(
            model_name='file',
            name='last_editor',
        ),
        migrations.RemoveField(
            model_name='file',
            name='size',
        ),
    ]
