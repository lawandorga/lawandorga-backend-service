# Generated by Django 3.1.6 on 2021-07-05 13:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('internal', '0007_auto_20210705_1542'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='roadmapitem',
            options={'ordering': ['date'], 'verbose_name': 'RoadmapItem', 'verbose_name_plural': 'RoadmapItems'},
        ),
    ]
