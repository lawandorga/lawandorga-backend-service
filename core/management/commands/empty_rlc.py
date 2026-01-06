from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from core.data_sheets.models import DataSheet
from core.files.models import File
from core.models import Org
from messagebus.domain.collector import EventCollector


def force_empty(org: Org):
    collector = EventCollector()
    for r in DataSheet.objects.filter(template__in=org.recordtemplates.all()):
        r.delete(collector=collector)
    for f in File.objects.filter(folder__in=org.folders.all()):
        f.delete()
    for fo in org.folders.all():
        fo.delete()
    for cnew in org.collabs.all():
        cnew.delete(collector=collector)
    for folder in org.folders_folders.all():
        folder.delete()
    for group in org.groups.all():
        group.delete()
    for record in org.records_records.all():
        record.delete(collector=collector)
    for template in org.questionnaire_templates.all():
        template.questionnaires.all().delete()
        template.delete()
    org.reset_keys()
    org.save()


class Command(BaseCommand):

    def handle(self, *args, **options):
        org_id = input("Enter the id of the org you want to empty: ")
        try:
            org = Org.objects.get(pk=org_id)
        except (ObjectDoesNotExist, ValueError):
            raise CommandError("No org was found with this id.")
        empty = input(
            "Do you want to empty org '{name}' with {records} records, "
            "{files} files and {collab} collab documents? [y/n]: ".format(
                **org.get_meta_information()
            )
        )
        empty = True if empty == "y" else False
        if empty:
            force_empty(org)
            self.stdout.write("The org '{}' was emptied.".format(org.name))
        else:
            self.stdout.write("No org was emptied.")
