# Generated by Django 3.2.12 on 2022-02-23 21:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0092_alter_note_note"),
        ("collab", "0008_remove_textdocumentversion_is_draft"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="collabdocument",
            unique_together={("rlc", "path")},
        ),
    ]
