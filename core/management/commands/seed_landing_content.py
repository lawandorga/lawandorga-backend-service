from datetime import date
from pathlib import Path
from typing import Any, Optional

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.internal.models import FeatureArea, RoadmapItem

# Texts taken verbatim from the design reference (source/Main.dc.html,
# renderVals: defs, more, roadmapLive, roadmapPlanned).

NOTE_DEMO_DATA = (
    "Screenshot aus der Demo-Organisation, Daten durch Beispieldaten ersetzt."
)

SHOWROOM: list[dict[str, Any]] = [
    {
        "title": "Akten",
        "description": "Alle Akten im Überblick: suchen, nach Tags und Status filtern und eigene Ansichten anlegen. Zugriff vergebt ihr an einzelne Personen oder Gruppen.",
        "icon": "ic-akten.png",
        "screenshot": "shot-akten.png",
        "screenshot_alt": "Screenshot: Aktenliste mit zehn Beispielakten, ihren Tags, Status, Beschreibung und Datum",
        "screenshot_note": NOTE_DEMO_DATA,
    },
    {
        "title": "Einzelne Akte",
        "description": "Alles zu einem Fall an einem Ort: Datenblätter mit eigenen Feldern und Vorlagen, Chat, Dateien, Fragebögen, Mail-Importe, Timeline und gemeinsame Dokumente. Offene Pflichtfelder werden angemahnt.",
        "icon": "ic-akten.png",
        "screenshot": "shot-akte.png",
        "screenshot_alt": "Screenshot: Einzelne Akte mit Datenblatt-Feldern wie Erstkontakt, Beschreibung des Anliegens, Berater:innen, Tags und Status sowie Bereichen für Chat, Dateien, Fragebögen, Mail-Importe, Timeline und Collabs",
        "screenshot_note": NOTE_DEMO_DATA,
    },
    {
        "title": "Aufgaben",
        "description": "Aufgaben mit einer oder mehreren zuständigen Personen, Prioritäten, Fortschritt, Tags und Kommentaren mit Zeitstempel. Mit # verlinkt ihr eine Akte direkt im Text.",
        "icon": "ic-tasks.png",
        "screenshot": "shot-tasks.png",
        "screenshot_alt": "Screenshot: Aufgabe „Widerspruch entwerfen“ mit zwei zuständigen Personen, Fortschritt 25 %, Priorität Medium und Tag Sozialrecht",
        "screenshot_note": NOTE_DEMO_DATA,
    },
    {
        "title": "Kalender",
        "description": "Tages-, Wochen-, Monats- und Listenansicht mit verschiedenen Terminarten. Freigabe für Personen, Gruppen oder die ganze Organisation mit Lese- und Bearbeitungsrechten pro Termin. Erinnerungen per E-Mail und Push, Export in externe Kalender.",
        "icon": "ic-kalender.png",
        "screenshot": "shot-kalender.png",
        "screenshot_alt": "Screenshot: Wochenansicht des Kalenders mit Terminen wie Erstberatung, Supervision und Teamtreffen sowie Filtern nach Terminart und Freigabe",
        "screenshot_note": NOTE_DEMO_DATA,
    },
    {
        "title": "Chat und Signal",
        "description": "Chat auf eigenem Matrix-Server, auch direkt in der Akte. Über die Signal-Bridge erreicht ihr Personen ohne Law&Orga-Zugang.",
        "icon": "ic-kommunikation.png",
        # no screenshot yet: the page shows the icon instead
        "screenshot": None,
        "screenshot_alt": "",
        "screenshot_note": "",
    },
    {
        "title": "Statistik",
        "description": "Nur für eure Organisation: offene, laufende und abgeschlossene Akten, Monats- und Jahresübersicht und eigene Auswertungen über Tags.",
        "icon": "ic-statistik.png",
        "screenshot": "shot-statistik.png",
        "screenshot_alt": "Ausschnitte aus der Statistik: Kreisdiagramme zu Geschlecht, Nationalität, Tags und Aktenstatus sowie ein Balkendiagramm zu angelegten und geschlossenen Akten",
        "screenshot_note": "Ausschnitte aus der Statistik der Demo-Organisation, neu angeordnet.",
    },
]

MORE: list[dict[str, Any]] = [
    {
        "title": "Dashboard und News",
        "description": "Ankündigungen für die ganze Organisation, Follow-ups und zuletzt bearbeitete Akten auf einen Blick.",
        "icon": "ic-dashboard.png",
        "screenshot": "shot-dashboard.png",
        "screenshot_alt": "Screenshot: Dashboard mit Fragebögen, Follow-ups, zuletzt bearbeiteten Akten und News",
        "screenshot_note": NOTE_DEMO_DATA,
    },
    {
        "title": "E-Mail und externe Anfragen",
        "description": "Eigener E-Mail-Betrieb über Law&Orga, Mailimport direkt in Akten und Dateien von Externen sicher per Link anfordern.",
        "icon": "ic-mail.png",
        "screenshot": None,
        "screenshot_alt": "",
        "screenshot_note": "",
    },
    {
        "title": "Admin-Bereich und Zugriffsrechte",
        "description": "Übersicht über Gruppen, Filter nach letztem Login und Aktivität. Rechte steuert ihr fein pro Person und Gruppe.",
        "icon": "ic-admin.png",
        "screenshot": "shot-admin.png",
        "screenshot_alt": "Screenshot: Admin-Bereich mit Profilen, Gruppen, Vorlagen, Sidebar und Organisationseinstellungen",
        "screenshot_note": "Screenshot aus der Demo-Organisation.",
    },
]

# live dates as confirmed by the project team, otherwise 01.01.2026
ROADMAP_LIVE: list[tuple[str, date]] = [
    ("Kalender mit Freigaben, Erinnerungen und Export", date(2026, 9, 11)),
    ("Signal-Bridge für den Chat", date(2026, 1, 1)),
    ("Neues Dashboard mit News", date(2026, 1, 1)),
    ("Überarbeitete Aufgaben mit mehreren Zuständigen", date(2026, 1, 1)),
    ("Gruppenzugriff auf einzelne Akten und Ordner", date(2026, 8, 27)),
    ("Erinnerung an offene Pflichtfelder in Akten", date(2026, 6, 7)),
    ("Akten per # in Aufgaben und Notizen verlinken", date(2026, 9, 11)),
]

# date of the design reference ("Stand")
ROADMAP_PLANNED_DATE = date(2026, 11, 20)

ROADMAP_PLANNED: list[dict[str, Any]] = [
    {
        "title": "Benachrichtigungen per E‑Mail und Push",
        "icon": "ic-bell.png",
        "stage": "Prototyp",
        "description": "Jede:r wählt im Profil selbst, worüber Law&Orga per E-Mail, Push oder beides informiert, getrennt nach Bereichen wie Dashboard, Aufgaben, Akten und Admin.",
        "benefits": [
            "Keine wichtige Änderung geht mehr unter",
            "Benachrichtigungen enthalten keine Inhalte aus Fallakten",
        ],
        "status_note": "Konzept und klickbarer Prototyp vorhanden.",
    },
    {
        "title": "L&O Share: Dateiaustausch zwischen Organisationen",
        "icon": "ic-share.png",
        "stage": "Prototyp",
        "description": "Sicherer Dateiaustausch und Wissensmanagement zwischen Organisationen, getrennt von den Fallakten. Ordner gehören einer oder mehreren Organisationen, Rechte gelten auch für Unterordner.",
        "benefits": [
            "Gemeinsame Vorlagen und Leitfäden an einem Ort",
            "Sichere Zusammenarbeit, z. B. zwischen Law Clinics und Flüchtlingsräten",
        ],
        "status_note": "Konzept und klickbarer Prototyp vorhanden.",
    },
    {
        "title": "L&O Forms: Formulare für Ratsuchende",
        "icon": "ic-forms.png",
        "stage": "Prototyp",
        "description": "Verschlüsselte Kontakt- und Erstberatungsformulare direkt in Law&Orga statt über externe Tools. Einsendungen lassen sich in eine Akte übernehmen.",
        "benefits": [
            "Keine Anfragen mehr über unsichere Formular-Dienste",
            "Weniger Abtippen bei der Aktenanlage",
        ],
        "status_note": "Umsetzungskonzept und Prototyp vorhanden.",
    },
]


class Command(BaseCommand):
    help = (
        "Create or update the landing page content (feature areas and roadmap). "
        "Idempotent: matches existing entries by title. New entries stay "
        "unpublished unless --publish is given."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--assets",
            type=str,
            default=None,
            help="Path to the assets folder of the design reference "
            "(contains icons/ and screenshots/). Images are only attached to "
            "entries that do not have one yet.",
        )
        parser.add_argument(
            "--publish",
            action="store_true",
            help="Publish the created or updated entries.",
        )

    def handle(self, *args, **options):
        assets: Optional[Path] = None
        if options["assets"]:
            assets = Path(options["assets"])
            if not (assets / "icons").is_dir() or not (assets / "screenshots").is_dir():
                raise CommandError(
                    "The assets folder needs the subfolders icons/ and screenshots/."
                )
        publish: bool = options["publish"]

        with transaction.atomic():
            for position, data in enumerate(SHOWROOM):
                self.seed_feature_area(
                    data, FeatureArea.PLACEMENT_SHOWROOM, position, assets, publish
                )
            for position, data in enumerate(MORE):
                self.seed_feature_area(
                    data, FeatureArea.PLACEMENT_MORE, position, assets, publish
                )
            for position, (title, live_date) in enumerate(ROADMAP_LIVE):
                self.seed_roadmap_item(
                    {
                        "title": title,
                        "date": live_date,
                        "status": RoadmapItem.STATUS_LIVE,
                    },
                    position,
                    None,
                    assets,
                    publish,
                )
            for position, data in enumerate(ROADMAP_PLANNED):
                self.seed_roadmap_item(
                    {
                        "title": data["title"],
                        "date": ROADMAP_PLANNED_DATE,
                        "status": RoadmapItem.STATUS_PLANNED,
                        "stage": data["stage"],
                        "description": data["description"],
                        "benefits": "\n".join(data["benefits"]),
                        "status_note": data["status_note"],
                    },
                    position,
                    data["icon"],
                    assets,
                    publish,
                )

        self.stdout.write(self.style.SUCCESS("Landing page content seeded."))

    def seed_feature_area(
        self,
        data: dict[str, Any],
        placement: str,
        position: int,
        assets: Optional[Path],
        publish: bool,
    ):
        defaults: dict[str, Any] = {
            "description": data["description"],
            "placement": placement,
            "position": position,
            "screenshot_alt": data["screenshot_alt"],
            "screenshot_note": data["screenshot_note"],
        }
        if publish:
            defaults["is_published"] = True
        area, created = FeatureArea.objects.update_or_create(
            title=data["title"], defaults=defaults
        )
        if assets is not None:
            changed = self.attach(area.icon, assets / "icons" / data["icon"])
            if data["screenshot"]:
                changed = (
                    self.attach(
                        area.screenshot, assets / "screenshots" / data["screenshot"]
                    )
                    or changed
                )
            if changed:
                area.full_clean()
                area.save()
        self.report("feature area", area.title, created)

    def seed_roadmap_item(
        self,
        defaults: dict[str, Any],
        position: int,
        icon: Optional[str],
        assets: Optional[Path],
        publish: bool,
    ):
        title = defaults.pop("title")
        defaults["position"] = position
        if publish:
            defaults["is_published"] = True
        item, created = RoadmapItem.objects.update_or_create(
            title=title, defaults=defaults
        )
        if assets is not None and icon is not None:
            if self.attach(item.icon, assets / "icons" / icon):
                item.save()
        self.report("roadmap item", item.title, created)

    def attach(self, field_file, path: Path) -> bool:
        """Attach the file at path to the image field, unless it has one."""
        if field_file:
            return False
        if not path.is_file():
            raise CommandError("File not found: {}".format(path))
        with path.open("rb") as f:
            field_file.save(path.name, File(f), save=False)
        return True

    def report(self, kind: str, title: str, created: bool):
        action = "created" if created else "updated"
        self.stdout.write("{} {}: {}".format(kind, action, title))
