from apps.recordmanagement.models import Tag, EncryptedRecord
from django.core.management import BaseCommand
from apps.api.models import Rlc

tags = [
    "Familiennachzug",
    "Dublin IV",
    "Arbeitserlaubnis",
    "Flüchtlingseigenschaft",
    "subsidiärer Schutz",
    "Eheschließung",
    "Verlobung",
    "illegale Ausreise aus dem Bundesgebiet",
    "Untertauchen",
    "Kinder anerkennen",
    "Ausbildung",
    "Geburt ",
    "Eines Kindes im Asylverfahren",
    "Duldung",
    "Ausbildungsduldung",
    "Visum",
    "Anhörung",
    "Wechsel der Unterkunft",
    "Wohnsitzauflage",
    "Folgeantrag",
    "Zweitantrag",
    "Unterbringung im Asylverfahren",
    "Widerruf der Asylberechtigung",
    "Rücknahme der Asyberechtigung",
    "Passbeschaffung",
    "Mitwirkungspflichten",
    "Nichtbetreiben des Verfahrens",
    "Krankheit im Asylverfahren",
    "Familienasyl",
    "UmF",
    "Familienzusammenführung nach Dublin III",
    "Negativbescheid",
    "Relocation",
    "Resettlement",
    "Asylbewerberleistungsgesetz",
    "Kirchenasyl",
    "Asylantrag",
    "Abschiebung",
    "Untätigkeitsklage",
    "Studium",
    "Strafverfolgung",
    "Sonstiges",
    "Geschwisternachzug",
    "Aufenthaltserlaubnis",
    "Aufenthaltsgestattung",
    "Niederlassungserlaubnis",
    "Einbürgerung",
    "Staatsbürgerschaft",
    "Übungsfall",
]


class Command(BaseCommand):
    help = "adds the old tags"

    def handle(self, *args, **options):
        print(len(tags))
        for rlc in Rlc.objects.all():
            for tag in tags:
                if not Tag.objects.filter(rlc=rlc, name=tag).exists():
                    Tag.objects.create(rlc=rlc, name=tag)
        print('tags finished')
        for record in EncryptedRecord.objects.all().order_by('pk'):
            print(record.id)
            for tag in record.tagged.all():
                record.tags.add(Tag.objects.get(name=tag.name, rlc=record.from_rlc))
