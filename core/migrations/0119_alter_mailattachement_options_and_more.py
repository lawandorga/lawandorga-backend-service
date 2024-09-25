# Generated by Django 5.0.8 on 2024-09-25 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0118_alter_template_uuid_mailattachement"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="mailattachement",
            options={
                "verbose_name": "MI_MailAttachment",
                "verbose_name_plural": "MI_MailAttachments",
            },
        ),
        migrations.RenameField(
            model_name="mailattachement",
            old_name="file_name",
            new_name="filename",
        ),
        migrations.AddField(
            model_name="mailattachement",
            name="content",
            field=models.FileField(null=True, upload_to="attachments"),
        ),
    ]
