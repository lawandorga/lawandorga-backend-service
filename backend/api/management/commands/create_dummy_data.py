#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
from backend.api.management.commands.fixtures import AddMethods
from backend.api.tests.fixtures_encryption import CreateFixtures as EncCreateFixtures
from django.core.management.base import BaseCommand
from backend.static import permissions
from backend.api.tests import example_data as ed
from .commands import (
    migrate_to_encryption,
    migrate_to_rlc_settings,
    populate_deploy_db,
    reset_db,
)
from backend.recordmanagement import models as record_models
from backend.api import models as api_models
import random


class Command(BaseCommand):
    help = "Populates database for deployment environment."

    def handle(self, *args, **options):
        # reset
        reset_db()
        populate_deploy_db()

        # create the dummy rlc
        rlc = ed.create_rlc()

        # create users
        users = ed.create_users(rlc)

        # create the dummy user you can login with to test everything
        dummy_users = ed.create_dummy_users(rlc)
        main_user = dummy_users[0]
        users = dummy_users + users

        # create inactive user
        mr_inactive = ed.create_inactive_user(rlc)

        # create groups
        groups = ed.create_groups(rlc, main_user, users)
        admin_group = ed.create_admin_group(rlc, main_user)

        # create clients
        clients = ed.create_clients(rlc)

        # create records
        records = ed.create_records(clients, users, rlc)
        # TODO: create best record
        best_record = self.create_the_best_record_ever(main_user, clients, users, rlc)

        # create requests
        self.create_record_deletion_request(main_user, best_record)
        self.create_record_permission_request(users[4], best_record)

        # TODO: delete later
        migrate_to_encryption()
        migrate_to_rlc_settings()

        # create notifications
        best_encrypted_record = record_models.EncryptedRecord.objects.filter(
            record_token=best_record.record_token
        ).first()
        groups_list = list(api_models.Group.objects.all())
        groups = [groups_list[0], groups_list[1]]
        Command.create_notifications(
            main_user, dummy_users[-1], best_encrypted_record, groups
        )

    def get_and_create_records(self, clients, consultants, rlc):
        tags = list(record_models.RecordTag.objects.all())
        records = [
            (
                random.choice(consultants),  # creator id
                (2018, 7, 12),  # created
                (2018, 8, 29, 13, 54, 0, 0),  # last edited
                clients[0],  # client
                (2018, 7, 10),  # first contact
                (2018, 8, 14, 17, 30, 0, 0),  # last contact
                "AZ-123/18",  # record token
                "informationen zum asylrecht",
                "cl",  # status, cl wa op
                [consultants[0], consultants[1]],  # working on
                [tags[0], tags[1]],  # tags
            ),
            (
                random.choice(consultants),
                (2018, 6, 23),
                (2018, 8, 22, 23, 3, 0, 0),
                clients[1],
                (2018, 6, 20),
                (2018, 7, 10, 17, 30, 0, 0),
                "AZ-124/18",
                "nicht abgeschlossen",
                "op",
                [consultants[0], consultants[2]],
                [tags[0], tags[12]],
            ),
            (
                random.choice(consultants),
                (2018, 8, 24),
                (2018, 8, 31, 1, 2, 0, 0),
                clients[2],
                (2018, 8, 22),
                (2018, 8, 22, 18, 30, 0, 0),
                "AZ-125/18",
                "auf Bescheid wartend",
                "wa",
                [consultants[0], consultants[3]],
                [tags[0], tags[11]],
            ),
            (
                random.choice(consultants),
                (2018, 3, 10),
                (2018, 4, 30, 19, 22, 0, 0),
                clients[3],
                (2018, 3, 9),
                (2018, 3, 24, 15, 54, 0, 0),
                "AZ-126/18",
                "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
                "cl",
                [consultants[0], consultants[4]],
                [tags[0], tags[10]],
            ),
            (
                random.choice(consultants),
                (2017, 9, 10),
                (2017, 10, 2, 15, 3, 0, 0),
                clients[4],
                (2017, 9, 10),
                (2017, 10, 2, 15, 3, 0, 0),
                "AZ-127/18",
                "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
                "cl",
                [consultants[0], consultants[5]],
                [tags[1], tags[2]],
            ),
            (
                random.choice(consultants),
                (2017, 9, 10),
                (2018, 9, 2, 16, 3, 0, 0),
                clients[5],
                (2017, 9, 10),
                (2018, 9, 2, 16, 3, 0, 0),
                "AZ-128/18",
                "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
                "wa",
                [consultants[1], consultants[2]],
                [tags[1], tags[3]],
            ),
            (
                random.choice(consultants),
                (2017, 9, 10),
                (2018, 1, 12, 16, 3, 0, 0),
                clients[6],
                (2017, 9, 10),
                (2018, 1, 12, 16, 3, 0, 0),
                "AZ-129/18",
                "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
                "op",
                [consultants[1], consultants[3]],
                [tags[2], tags[4]],
            ),
            (
                random.choice(consultants),
                (2017, 9, 10),
                (2018, 1, 2, 16, 3, 0, 0),
                clients[7],
                (2017, 9, 10),
                (2018, 1, 2, 16, 3, 0, 0),
                "AZ-130/18",
                "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
                "cl",
                [consultants[2], consultants[5]],
                [tags[1], tags[5]],
            ),
            (
                random.choice(consultants),
                (2017, 9, 10),
                (2018, 12, 2, 16, 3, 0, 0),
                clients[8],
                (2017, 9, 10),
                (2018, 12, 2, 16, 3, 0, 0),
                "AZ-131/18",
                "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
                "wa",
                [consultants[3], consultants[4]],
                [tags[0], tags[7]],
            ),
            (
                random.choice(consultants),
                (2017, 9, 10),
                (2018, 10, 2, 16, 3, 0, 0),
                clients[9],
                (2017, 9, 10),
                (2018, 10, 2, 16, 3, 0, 0),
                "AZ-132/18",
                "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
                "op",
                [consultants[5], consultants[4]],
                [tags[3], tags[4]],
            ),
            (
                random.choice(consultants),
                (2017, 9, 10),
                (2018, 10, 2, 16, 3, 0, 0),
                clients[0],
                (2017, 9, 10),
                (2018, 10, 2, 16, 3, 0, 0),
                "AZ-139/18",
                "zweite akte von client 0",
                "op",
                [consultants[5], consultants[4]],
                [tags[3], tags[4]],
            ),
        ]
        records_in_db = []
        for rec in records:
            # records_in_db.append(self.get_and_create_record(rec, rlc))
            record = record_models.Record(
                from_rlc=rlc,
                creator=rec[0],
                client=rec[3],
                record_token=rec[6],
                official_note=rec[7],
                state=rec[8],
            )
            record.created_on = AddMethods.generate_date(rec[1])
            record.first_contact_date = AddMethods.generate_date(rec[4])
            record.last_edited = AddMethods.generate_datetime(rec[2])
            record.last_contact_date = AddMethods.generate_datetime(rec[5])
            record.save()
            for user in rec[9]:
                record.working_on_record.add(user)
            for tag in rec[10]:
                record.tagged.add(tag)
            record.save()
            records_in_db.append(record)
        return records_in_db

    def create_the_best_record_ever(self, main_user, clients, consultants, rlc):
        tags = list(record_models.RecordTag.objects.all())
        record = record_models.Record(
            from_rlc=rlc,
            creator=main_user,
            client=clients[0],
            record_token="AZ-001/18",
            official_note="best record ever",
            state="op",
            id=7181,
        )

        record.created_on = AddMethods.generate_date((2018, 1, 3))
        record.first_contact_date = AddMethods.generate_date((2018, 1, 3))
        record.last_edited = AddMethods.generate_datetime((2019, 3, 11, 9, 32, 21, 0))
        record.last_contact_date = AddMethods.generate_datetime(
            (2019, 2, 28, 17, 33, 0, 0)
        )
        record.first_consultation = AddMethods.generate_datetime(
            (2018, 1, 2, 23, 55, 0, 0)
        )
        record.note = "Mandant moechte dass wir ihn vor Gericht vertreten. Das duerfen wir aber nicht. #RDG"
        record.consultant_team = "Taskforce 417"
        record.lawyer = "RA Guenther-Klaus, Kiesweg 3"
        record.related_persons = "Sozialarbeiter Apfel (Direkt in der Unterkunft)"
        record.contact = "Mail: asksk1@bmw.de,\n Telefon: 0800 444 55 444"
        record.bamf_token = "QRS-232/2018"
        record.foreign_token = "Vor Gericht: FA93932-1320"
        record.first_correspondence = (
            "Hallo Liebes Team der RLC,\n ich habe folgendes Problem.\nKoennt ihr mir "
            "helfen?\n Vielen Dank"
        )
        record.circumstances = "Kam ueber die Balkanroute, Bruder auf dem Weg verloren, wenig Kontakt zu Familie."
        record.next_steps = "Klae einreichen und gewinnen!"
        record.status_described = (
            "Auf Antwort wartend, anschliessend weitere Bearbeitung."
        )
        record.additional_facts = "Hat noch nie ne Schweinshaxe gegessen."

        record.save()
        record.working_on_record.add(consultants[0], main_user)
        record.tagged.add(tags[0], tags[1])
        record.save()

        document1 = record_models.RecordDocument(
            name="7_1_19__pass.jpg", creator=main_user, record=record, file_size=18839
        )
        document1.created_on = AddMethods.generate_date((2019, 1, 7))
        document1.save()
        document1.tagged.add(record_models.RecordDocumentTag.objects.get(name="Pass"))

        document2 = record_models.RecordDocument(
            name="3_10_18__geburtsurkunde.pdf",
            creator=main_user,
            record=record,
            file_size=488383,
        )
        document2.created_on = AddMethods.generate_date((2018, 10, 3))
        document2.save()
        document2.tagged.add(
            record_models.RecordDocumentTag.objects.get(name="Geburtsurkunde")
        )

        document3 = record_models.RecordDocument(
            name="3_12_18__Ablehnungbescheid.pdf",
            creator=main_user,
            record=record,
            file_size=343433,
        )
        document3.created_on = AddMethods.generate_date((2018, 12, 3))
        document3.save()
        document3.tagged.add(
            record_models.RecordDocumentTag.objects.get(name="Bescheid (Ablehnung)")
        )

        document4 = record_models.RecordDocument(
            name="1_1_19__Klageschrift.docx",
            creator=main_user,
            record=record,
            file_size=444444,
        )
        document4.save()
        document4.created_on = AddMethods.generate_date((2019, 1, 1))

        message = record_models.RecordMessage(
            sender=main_user,
            record=record,
            message="Bitte dringend die Kontaktdaten des Mandanten eintragen.",
        )
        message.save()
        message.created_on = AddMethods.generate_datetime((2019, 3, 11, 10, 12, 21, 0))
        message.save()
        message = record_models.RecordMessage(
            sender=consultants[0],
            record=record,
            message="Ist erledigt! Koennen wir uns morgen treffen um das zu besprechen?",
        )
        message.save()
        message.created_on = AddMethods.generate_datetime((2019, 3, 12, 9, 32, 21, 0))
        message.save()
        message = record_models.RecordMessage(
            sender=main_user,
            record=record,
            message="Klar, einfach direkt in der Mittagspause in der Mensa.",
        )
        message.save()
        message.created_on = AddMethods.generate_datetime((2019, 3, 12, 14, 7, 21, 0))
        message.save()
        message = record_models.RecordMessage(
            sender=consultants[0],
            record=record,
            message="Gut, jetzt faellt mir aber auch nichts mehr ein.",
        )
        message.save()
        message.created_on = AddMethods.generate_datetime((2019, 3, 13, 18, 7, 21, 0))
        message.save()
        return record

    def create_record_deletion_request(self, user, record):
        request = record_models.RecordDeletionRequest(
            record=record, request_from=user, state="re"
        )
        request.save()

    def create_record_permission_request(self, user: api_models.UserProfile, record):
        request = record_models.RecordPermission(
            record=record, request_from=user, state="re"
        )
        request.save()

    @staticmethod
    def create_notifications(
        user: api_models.UserProfile,
        source_user: api_models.UserProfile,
        record: record_models.EncryptedRecord,
        groups: [api_models.Group],
    ):
        EncCreateFixtures.add_notification_fixtures(
            main_user=user,
            source_user=source_user,
            records=[record, record],
            groups=groups,
        )
