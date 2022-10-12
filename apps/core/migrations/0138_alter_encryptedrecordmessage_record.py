# Generated by Django 4.0.7 on 2022-10-12 12:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0137_alter_recordencryptionnew_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='encryptedrecordmessage',
            name='record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='core.record'),
        ),
    ]
