#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
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
from backend.api.models import Rlc, Group, HasPermission, Permission, permissions
from backend.api.models import UserProfile
from datetime import date
from random import randint, choice

# helpers
from backend.recordmanagement.models import OriginCountry, EncryptedClient, RecordTag, EncryptedRecord


def add_permissions_to_group(group: Group, permission_name):
    HasPermission.objects.create(
        group_has_permission=group,
        permission_for_rlc=group.from_rlc,
        permission=Permission.objects.get(name=permission_name),
    )


# create
def create_rlc():
    return Rlc.objects.create(
        name="Dummy RLC",
        note="This is a dummy rlc, just for showing how the system works.",
        id=3033
    )


def create_users(rlc):
    users = [
        (
            "ludwig.maximilian@outlook.de",
            "Ludwig Maximilian",
            (1985, 5, 12),
            "01732421123",
            "Maximilianstrasse 12",
            "München",
            "80539",
        ),
        (
            "xxALIxxstone@hotmail.com",
            "Albert Einstein",
            (1879, 3, 14),
            "01763425656",
            "Blumengasse 23",
            "Hamburg",
            "83452",
        ),
        (
            "mariecurry53@hotmail.com",
            "Marie Curie",
            (1867, 11, 7),
            "0174565656",
            "Jungfernstieg 2",
            "Hamburg",
            "34264",
        ),
        (
            "max.mustermann@gmail.com",
            "Maximilian Gustav Mustermann",
            (1997, 10, 23),
            "0176349756",
            "Schlossallee 100",
            "Grünwald",
            "82031",
        ),
        (
            "petergustav@gmail.com",
            "Peter Klaus Gustav von Guttenberg",
            (1995, 3, 11),
            "01763423732",
            "Leopoldstrasse 31",
            "Muenchen",
            "80238",
        ),
        (
            "gabi92@hotmail.com",
            "Gabriele Schwarz",
            (1998, 12, 10),
            "0175647332",
            "Kartoffelweg 12",
            "Muenchen",
            "80238",
        ),
        (
            "rudi343@gmail.com",
            "Rudolf Mayer",
            (1996, 5, 23),
            "01534423732",
            "Barerstrasse 3",
            "Muenchen",
            "80238",
        ),
        (
            "lea.g@gmx.com",
            "Lea Glas",
            (1985, 7, 11),
            "01763222732",
            "Argentinische Allee 34",
            "Hamburg",
            "34264",
        ),
        (
            "butterkeks@gmail.com",
            "Bettina Rupprecht",
            (1995, 10, 11),
            "01765673732",
            "Ordensmeisterstrasse 56",
            "Hamburg",
            "34264",
        ),
        (
            "willi.B@web.de",
            "Willi Birne",
            (1997, 6, 15),
            "01763425555",
            "Grunewaldstrasse 45",
            "Hamburg",
            "34264",
        ),
        (
            "pippi.langstrumpf@gmail.com",
            "Pippi Langstumpf",
            (1981, 7, 22),
            "01766767732",
            "Muehlenstraße 12",
            "Muenchen",
            "80238",
        ),
    ]

    created_users = []
    for user in users:
        birthday = users[2]
        created_users.append(
            UserProfile.objects.create(
                email=user[0],
                name=user[1],
                phone_number=user[3],
                street=user[4],
                city=user[5],
                postal_code=user[6],
                birthday=date(*birthday),
                rlc=rlc,
            )
        )
    return created_users


def create_dummy_users(rlc: Rlc):
    users = []

    # main user
    user = UserProfile.objects.create(
        name="Mr Dummy",
        email="dummy@rlcm.de",
        phone_number="01666666666",
        street="Dummyweg 12",
        city="Dummycity",
        postal_code="00000",
        rlc=rlc,
        birthday=(1995, 1, 1)
    )
    user.set_password("qwe123")
    user.save()
    users.append(user)

    # other dummy users
    user = UserProfile.objects.create(
        name="Tester 1",
        email="tester1@law-orga.de",
        phone_number="123812382",
        rlc=rlc,
    )
    user.set_password("qwe123")
    user.save()
    users.append(user)

    user = UserProfile.objects.create(
        name="Tester 2",
        email="tester2@law-orga.de",
        phone_number="123812383",
        rlc=rlc,
    )
    user.set_password("qwe123")
    user.save()
    users.append(user)

    # return
    return users


def create_inactive_user(rlc):
    user = UserProfile(
        name="Mr. Inactive",
        email="inactive@rlcm.de",
        phone_number="1293283882",
        street="Inaktive Strasse",
        city="InAktiv",
        postal_code="29292",
        rlc=rlc,
        birthday=(1950, 1, 1)
    )
    user.set_password("qwe123")
    user.is_active = False
    user.save()


def create_groups(rlc: Rlc, creator: UserProfile, users: [UserProfile]):
    # create consultants group
    consultants_group = Group.objects.create(
        creator=creator,
        from_rlc=rlc,
        name="Berater",
        visible=False,
        description="all consultants",
        note="only add consultants",
    )

    for i in range(0, randint(0, len(users))):
        consultants_group.group_members.add(users[i])

    add_permissions_to_group(consultants_group, permissions.PERMISSION_CAN_CONSULT)
    add_permissions_to_group(consultants_group, permissions.PERMISSION_VIEW_RECORDS_RLC)

    # create ag group
    ag_group = Group.objects.create(
        creator=users[0],
        from_rlc=rlc,
        name="AG Datenschutz",
        visible=True,
        description="DSGVO",
        note="bitte mithelfen",
    )

    for i in range(0, randint(0, int(len(users) / 2))):
        ag_group.group_members.add(users[i])

    # return
    return [consultants_group, ag_group]


def create_admin_group(rlc: Rlc, main_user: UserProfile):
    # create admin group
    admin_group = Group.objects.create(
        creator=main_user,
        from_rlc=rlc,
        name="Administratoren",
        visible=False,
        description="haben alle Berechtigungen",
        note="IT ressort",
    )
    admin_group.group_members.add(main_user)

    add_permissions_to_group(admin_group, permissions.PERMISSION_VIEW_PERMISSIONS_RLC)
    add_permissions_to_group(admin_group, permissions.PERMISSION_MANAGE_PERMISSIONS_RLC)
    add_permissions_to_group(admin_group, permissions.PERMISSION_MANAGE_GROUPS_RLC)
    add_permissions_to_group(admin_group, permissions.PERMISSION_ACCEPT_NEW_USERS_RLC)
    add_permissions_to_group(admin_group, permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC)
    add_permissions_to_group(admin_group, permissions.PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC)
    add_permissions_to_group(admin_group, permissions.PERMISSION_VIEW_RECORDS_RLC)

    # return
    return admin_group


def create_clients(rlc: Rlc):
    origin_countries = OriginCountry.objects.all()
    clients = [
        (
            (2018, 7, 12),  # created_on
            (2018, 8, 28, 21, 3, 0, 0),  # last_edited
            "Bibi Aisha",  # name
            "auf Flucht von Ehemann getrennt worden",  # note
            "01793456542",  # phone number
            (1990, 5, 1),  # birthday
            choice(origin_countries),  # origin country id
        ),
        (
            (2017, 3, 17),
            (2017, 12, 24, 12, 2, 0, 0),
            "Mustafa Kubi",
            "möchte eine Ausbildung beginnen",
            None,
            (1998, 12, 3),
            choice(origin_countries),
        ),
        (
            (2018, 1, 1),
            (2018, 3, 3, 14, 5, 0, 0),
            "Ali Baba",
            "fragt wie er seine deutsche Freundin heiraten kann",
            "",
            (1985, 6, 27),
            choice(origin_countries),
        ),
        (
            (2018, 8, 1),
            (2018, 8, 2, 16, 3, 0, 0),
            "Kamila Iman",
            "möchte zu ihrer Schwester in eine andere Aufnahmeeinrichtung ziehen",
            "01562736778",
            (1956, 4, 3),
            choice(origin_countries),
        ),
        (
            (2017, 9, 10),
            (2017, 10, 2, 15, 3, 0, 0),
            "Junis Haddad",
            "Informationen zum Asylverfahren",
            "013345736778",
            (1998, 6, 2),
            choice(origin_countries),
        ),
        (
            (2017, 9, 10),
            (2018, 9, 2, 16, 3, 0, 0),
            "Nael Mousa",
            "Informationen zum Asylverfahren",
            "01444436778",
            (1997, 6, 4),
            choice(origin_countries),
        ),
        (
            (2017, 9, 10),
            (2018, 1, 12, 16, 3, 0, 0),
            "Amir Hamdan",
            "Informationen zum Asylverfahren",
            "01457636778",
            (1996, 6, 8),
            choice(origin_countries),
        ),
        (
            (2017, 9, 10),
            (2018, 1, 2, 16, 3, 0, 0),
            "Amar Yousef",
            "Informationen zum Asylverfahren",
            "01566546778",
            (1995, 5, 10),
            choice(origin_countries),
        ),
        (
            (2017, 9, 10),
            (2017, 12, 2, 16, 3, 0, 0),
            "Tarek Habib",
            "Informationen zum Asylverfahren",
            "013564736778",
            (1994, 5, 12),
            choice(origin_countries),
        ),
        (
            (2017, 9, 10),
            (2018, 10, 2, 16, 3, 0, 0),
            "Kaya Yousif",
            "Informationen zum Asylverfahren",
            "01564586778",
            (1993, 4, 14),
            choice(origin_countries),
        ),
    ]
    created_clients = []

    for client in clients:
        created_client = EncryptedClient(
            name=client[2],
            from_rlc=rlc,
            created_on=client[0],
            last_edited=client[1],
            birthday=client[5],
            origin_country=client[6],
            note=client[3],
            phone_number=client[4],
        )
        created_client.encrypt(rlc.get_public_key())
        created_client.save()
        created_clients.append(created_client)

    return created_clients


def create_records(clients, consultants, rlc):
    assert len(clients) > 9
    assert len(consultants) > 5

    tags = RecordTag.objects.all()
    records = [
        (
            choice(consultants),  # creator id
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
            choice(consultants),
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
            choice(consultants),
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
            choice(consultants),
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
            choice(consultants),
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
            choice(consultants),
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
            choice(consultants),
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
            choice(consultants),
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
            choice(consultants),
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
            choice(consultants),
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
            choice(consultants),
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

    created_records = []
    for record in records:
        created_record = EncryptedRecord(
            from_rlc=rlc,
            creator=record[0],
            client=record[3],
            record_token=record[6],
            official_note=record[7],
            state=record[8],
            created_on=record[1],
            first_contact_date=record[4],
            last_edited=record[2],
            last_contact_date=record[5]
        )
        created_record.encrypt()
        for user in records[9]:
            created_record.working_on_record.add(user)
        for tag in records[10]:
            created_record.tagged.add(tag)
        record.save()
        created_records.append(record)
    return created_records
