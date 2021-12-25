# Generated by Django 3.2.9 on 2021-12-23 18:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recordmanagement', '0082_rename_record_encryptedrecordmessage_old_record'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='encryptedrecordmessage',
            options={'ordering': ['created'], 'verbose_name': 'RecordMessage', 'verbose_name_plural': 'RecordMessages'},
        ),
        migrations.RenameField(
            model_name='encryptedrecordmessage',
            old_name='created_on',
            new_name='created',
        ),
        migrations.AddField(
            model_name='encryptedrecordmessage',
            name='record',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='recordmanagement.record'),
        ),
        migrations.AddField(
            model_name='encryptedrecordmessage',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
