#  rlcapp - record and organization management software for refugee law clinics
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

from datetime import date, datetime

import pytz
from django.conf import settings

from backend.api.tests import *
from backend.recordmanagement.models import RecordTag, Record, OriginCountry, Client, RecordDocumentTag
from backend.static.permissions import get_all_permissions


class Fixtures:
    @staticmethod
    def create_example_static_users():
        user = UserProfile(id=1, email='abc@web.de', name='Betsy', is_active=True)
        user.set_password('qwe123')
        user.save()

        user = UserProfile(id=2, email='jehob@web.de', name='Peter', is_active=True, is_superuser=True)
        user.set_password('qwe123')
        user.save()

    @staticmethod
    def create_example_record_tags():
        tags = [('Dublin III',), ('family reunion',), ('asylum',), ('stay',), ('employment',)]
        for single_tag in tags:
            AddMethods.add_record_tag(single_tag)

    @staticmethod
    def create_example_origin_countries():
        countries = [('Botswana', 'st'), ('Ghana', 'ot'), ('Nigeria', 'so'),
                     ('Turkey', 'so'), ('Sahara', 'ot'), ('Ukraine', 'st'),
                     ('Syria', 'ot')]
        for country in countries:
            AddMethods.add_country(country)

    @staticmethod
    def create_real_origin_countries():
        countries = [('Abchasien',), ('Afghanistan',), ('Ägypten',), ('Albanien',), ('Algerien',), ('Andorra',), (
            'Angola',), ('Antigua und Barbuda',), ('Äquatorialguinea',), ('Argentinien',), ('Armenien',), ('Arzach',), (
                         'Aserbaidschan',), ('Äthiopien',), ('Australien',), ('Bahamas',), (
                         'Bahrain',), ('Bangladesch',), ('Barbados',), ('Belgien',), ('Belize',), (
                         'Benin',), ('Bhutan',), ('Bolivien',), ('Bosnien und Herzegowina',), (
                         'Botswana',), ('Brasilien',), ('Brunei',), ('Bulgarien',), ('Burkina Faso',), (
                         'Burundi',), ('Chile',), ('Republik China',), ('Volksrepublik China',), (
                         'Cookinseln',), ('Costa Rica',), ('Dänemark',), ('Deutschland',), ('Dominica',), (
                         'Dominikanische Republik',), ('Dschibuti',), ('Ecuador',), ('El Salvador',), (
                         'Elfenbeinküste',), ('Eritrea',), ('Estland',), ('Fidschi',), ('Finnland',), (
                         'Frankreich',), ('Gabun',), ('Gambia',), ('Georgien',), ('Ghana',), (
                         'Grenada',), ('Griechenland',), ('Guatemala',), ('Guinea',), (
                         'Guinea-Bissau',), ('Guyana',), ('Haiti',), ('Honduras',), ('Indien',), (
                         'Indonesien',), ('Irak',), ('Iran',), ('Irland',), ('Island',), ('Israel',), (
                         'Italien',), ('Jamaika',), ('Japan',), ('Jemen',), ('Jordanien',), (
                         'Kambodscha',), ('Kamerun',), ('Kanada',), ('Kap Verde',), ('Kasachstan',), (
                         'Katar',), ('Kenia',), ('Kirgisistan',), ('Kiribati',), ('Kolumbien',), (
                         'Komoren',), ('Kongo, Demokratische Republik',), ('Kongo, Republik',), (
                         'Nordkorea',), ('Südkorea',), ('Kosovo',), ('Kroatien',), ('Kuba',), (
                         'Kuwait',), ('Laos',), ('Lesotho',), ('Lettland',), ('Libanon',), (
                         'Liberia',), ('Libyen',), ('Liechtenstein',), ('Litauen',), ('Luxemburg',), (
                         'Madagaskar',), ('Malawi',), ('Malaysia',), ('Malediven',), ('Mali',), (
                         'Malta',), ('Marokko',), ('Marshallinseln',), ('Mauretanien',), ('Mauritius',), (
                         'Mexiko',), ('Mikronesien',), ('Moldau',), ('Monaco',), ('Mongolei',), (
                         'Montenegro',), ('Mosambik',), ('Myanmar',), ('Namibia',), ('Nauru',), (
                         'Nepal',), ('Neuseeland',), ('Nicaragua',), ('Niederlande',), ('Curaçao',), (
                         'Sint Maarten',), ('Niger',), ('Nigeria',), ('Niue',), ('Nordmazedonien',), (
                         'Nordzypern',), ('Norwegen',), ('Oman',), ('Österreich',), (
                         'Osttimor / Timor-Leste',), ('Pakistan',), ('Palästina',), ('Palau',), (
                         'Panama',), ('Papua-Neuguinea',), ('Paraguay',), ('Peru',), ('Philippinen',), (
                         'Polen',), ('Portugal',), ('Ruanda',), ('Rumänien',), ('Russland',), (
                         'Salomonen',), ('Sambia',), ('Samoa',), ('San Marino',), (
                         'São Tomé und Príncipe',), ('Saudi-Arabien',), ('Schweden',), ('Schweiz',), (
                         'Senegal',), ('Serbien',), ('Seychellen',), ('Sierra Leone',), ('Simbabwe',), (
                         'Singapur',), ('Slowakei',), ('Slowenien',), ('Somalia',), ('Somaliland',), (
                         'Spanien',), ('Sri Lanka',), ('St. Kitts und Nevis',), ('St. Lucia',), (
                         'St. Vincent und die Grenadinen',), ('Südafrika',), ('Sudan',), (
                         'Südossetien',), ('Südsudan',), ('Suriname',), ('Swasiland',), ('Syrien',), (
                         'Tadschikistan',), ('Tansania',), ('Thailand',), ('Togo',), ('Tonga',), (
                         'Transnistrien',), ('Trinidad und Tobago',), ('Tschad',), ('Tschechien',), (
                         'Tunesien',), ('Türkei',), ('Turkmenistan',), ('Tuvalu',), ('Uganda',), (
                         'Ukraine',), ('Ungarn',), ('Uruguay',), ('Usbekistan',), ('Vanuatu',), (
                         'Vatikanstadt',), ('Venezuela',), ('Vereinigte Arabische Emirate',), (
                         'Vereinigte Staaten',), ('Vereinigtes Königreich',), ('Vietnam',), (
                         'Weißrussland',), ('Westsahara',), ('Zentral­afrikanische Republik',), (
                         'Zypern',)]
        for country in countries:
            AddMethods.add_country(country)

    @staticmethod
    def create_example_permissions():
        permissions = [('add_records',), ('edit_records',), ('remove_records',), ('view_records',), ('view_users',),
                       ('view_records_full_detail',), ('can_consult',)]
        real_perms = get_all_permissions()
        for rperm in real_perms:
            if (rperm,) not in permissions:
                permissions.append((rperm,))

        for perm in permissions:
            AddMethods.add_permission(perm)

    @staticmethod
    def create_rlcs():
        rlcs = ((1, 'RLC Muenchen', False, True),
                (2, 'RLC Hamburg', False, True),
                (3, 'RLC Leipzig', False, True))
        for rlc in rlcs:
            AddMethods.add_rlc(rlc)

    @staticmethod
    def create_real_permissions():
        permissions = get_all_permissions()
        for permission in permissions:
            AddMethods.add_permission(permission)

    @staticmethod
    def create_real_permissions_no_duplicates():
        permissions = get_all_permissions()
        for permission in permissions:
            if Permission.objects.filter(name=permission).count() == 0:
                AddMethods.add_permission(permission)

    @staticmethod
    def create_real_tags():
        tags = [('Familiennachzug',), ('Dublin IV',), ('Arbeitserlaubnis',), ('Flüchtlingseigenschaft',),
                ('subsidiärer Schutz',), ('Eheschließung',), ('Verlobung',),
                ('illegale Ausreise aus dem Bundesgebiet',), ('Untertauchen',), ('Kinder anerkennen',), ('Ausbildung',),
                ('Geburt ',), ('Eines Kindes im Asylverfahren',), ('Duldung',), ('Ausbildungsduldung',), ('Visum',),
                ('Anhörung',), ('Wechsel der Unterkunft',), ('Wohnsitzauflage',), ('Folgeantrag',), ('Zweitantrag',),
                ('Unterbringung im Asylverfahren',), ('Widerruf der Asylberechtigung',), ('Rücknahme der Asyberechtigung',),
                ('Passbeschaffung',), ('Mitwirkungspflichten',), ('Nichtbetreiben des Verfahrens',),
                ('Krankheit im Asylverfahren',), ('Familienasyl',), ('UmF',),
                ('Familienzusammenführung nach Dublin III',), ('Negativbescheid',), ('Relocation',), ('Resettlement',),
                ('Asylbewerberleistungsgesetz',), ('Kirchenasyl',), ('Asylantrag',), ('Abschiebung',),
                ('Untätigkeitsklage',), ('Studium',), ('Strafverfolgung',),]
        for tag in tags:
            AddMethods.add_record_tag(tag)

    @staticmethod
    def create_real_document_tags():
        tags = [('Pass',), ('Passersatzpapier',), ('Geburtsurkunde',), ('Heiratsurkunde',), ('Ankunftsnachweis',),
                ('Duldung',), ('Aufenthaltsgestattung',), ('Aufenthaltstitel',), ('Bescheid (Ablehnung)',),
                ('Bescheid (Flüchtling)',), ('Bescheid (subsidiärer Schutz)',), ('Bescheid (Abschiebeverbote)',),
                ('Bescheid (Sozialleistungen)',), ('Bescheid (Arbeiten)',), ('Bescheid (Wohnen)',),
                ('Widerspruch',), ('Antwortschreiben',), ('Erwiderung',), ('Sachstandsanfrage',), ('Klageschrift',),
                ('Akteneinsicht',), ('Anfrage',), ('Terminvereinbarung',), ('Attest',), ('Verschwiegenheitserklärung',),
                ('Datenschutzerklärung',), ('Erklärung',), ('Vertrag',), ('Antrag',), ('Zeugnis',),
                ('Zertifikat',), ('Vollmacht',), ('Anhörungsvorbereitung',), ]
        for tag in tags:
            AddMethods.add_record_document_tag(tag)

    @staticmethod
    def create_real_starting_rlcs():
        rlcs = (('RLC München', False, True),
                ('RLC Hamburg', False, True))
        for rlc in rlcs:
            AddMethods.add_rlc(rlc)
        return list(Rlc.objects.all())

    @staticmethod
    def create_real_groups(rlcs):
        groups = [('Members', False),
                  ('Admins', False),
                  ('Consultants', False)]
        for rlc in rlcs:
            for group in groups:
                AddMethods.add_group(group, rlc.id)
        return list(Group.objects.all())

    @staticmethod
    def create_good_example_records():
        r = Record(creator_id=1, from_rlc_id=1, created_on=date(2017, 12, 24),
                   last_edited=datetime(2018, 4, 12, 13, 56, 0, 0), client=1, first_contact_date=date(2017, 12, 24),
                   last_contact_date=datetime(2018, 4, 12, 18, 30, 0, 0), record_token='AZ-MUC-14/28',
                   note='was in italy before', state='op')
        r.tagged.add(12)
        r.working_on_record.add(1)
        r.save()

    @staticmethod
    def create_handmade_examples():
        record_tags = [(1001, 'Familiennachzug'),
                       (1002, 'Ausbildung'),
                       (1003, 'Anhörung'),
                       (1004, 'Abschiebung'),
                       (1005, 'Asylantrag')
                       ]
        for tag in record_tags:
            AddMethods.add_record_tag(tag)

        record_document_tags = [(120001, 'Official Document'),
                                (120002, 'Pleading'),
                                (120004, 'Proof'),
                                (120003, 'Passport')]
        for tag in record_document_tags:
            AddMethods.add_record_document_tag(tag)

        countries = [(2001, 'Italien', 'ot'),
                     (2002, 'Syrien', 'so'),
                     (2003, 'Norwegen', 'st'),
                     (2004, 'Bulgarien', 'ot'),
                     (2005, 'Spanien', 'ot'),
                     (2006, 'Griechenland', 'ot'),
                     (2007, 'Irak', 'so'),
                     (2008, 'Iran', 'so'),
                     (2009, 'Afghanistan', 'so'),
                     (2010, 'Nigeria', 'st')
                     ]
        for country in countries:
            AddMethods.add_country(country)

        rlcs = [
            (
                3001,
                'Hamburg Bucerius Law School',
                True,  # visible
                True,  # part of umbrella
                'beraten auch zu Familienrecht, Sozialrecht und Arbeitsrecht'
            ),
            (
                3002,
                'Hamburg Universität',
                True,
                True,
                'bieten Anhörungsvorbereitung, Studierende können zum Teil Farsi und Arabisch'
            ),
            (
                3003,
                'München',
                False,
                True,
                'gut organisiertes Ausbildungsprogramm'
            )
        ]
        for rlc in rlcs:
            AddMethods.add_rlc(rlc)

        users = [
            (
                4001,
                'ludwig.maximilian@outlook.de',
                'Ludwig Maximilian',
                (1985, 5, 12),  # birthday
                '01732421123',
                'Maximilianstrasse 12',
                'München',
                '80539',
                3003  # rlc_member
            ),
            (
                4002,
                'xxALIxxstone@hotmail.com',
                'Albert Einstein',
                (1879, 3, 14),
                '01763425656',
                'Blumengasse 23',
                'Hamburg',
                '83452',
                3001
            ),
            (
                4003,
                'mariecurry53@hotmail.com',
                'Marie Curie',
                (1867, 11, 7),
                '0174565656',
                'Jungfernstieg 2',
                'Hamburg',
                '34264',
                3001
            ),
            (
                4004,
                'max.mustermann@gmail.com',
                'Maximilian Gustav Mustermann',
                (1997, 10, 23),
                '0176349756',
                'Schlossallee 100',
                'Grünwald',
                '82031',
                3003
            ),
            (
                4005,
                'petergustav@gmail.com',
                'Peter Klaus Gustav von Guttenberg',
                (1995, 3, 11),
                '01763423732',
                'Leopoldstrasse 31',
                'Muenchen',
                '80238',
                3003
            ),
            (
                4006,
                'gabi92@hotmail.com',
                'Gabriele Schwarz',
                (1998, 12, 10),
                '0175647332',
                'Kartoffelweg 12',
                'Muenchen',
                '80238',
                3002
            ),
            (
                4007,
                'rudi343@gmail.com',
                'Rudolf Mayer',
                (1996, 5, 23),
                '01534423732',
                'Barerstrasse 3',
                'Muenchen',
                '80238',
                3002
            ),
            (
                4008,
                'lea.g@gmx.com',
                'Lea Glas',
                (1985, 7, 11),
                '01763222732',
                'Argentinische Allee 34',
                'Hamburg',
                '34264',
                3003
            ),
            (
                4009,
                'butterkeks@gmail.com',
                'Bettina Rupprecht',
                (1995, 10, 11),
                '01765673732',
                'Ordensmeisterstrasse 56',
                'Hamburg',
                '34264',
                3001
            ),
            (
                4010,
                'willi.B@web.de',
                'Willi Birne',
                (1997, 6, 15),
                '01763425555',
                'Grunewaldstrasse 45',
                'Hamburg',
                '34264',
                3001
            ),
            (
                4011,
                'pippi.langstrumpf@gmail.com',
                'Pippi Langstumpf',
                (1981, 7, 22),
                '01766767732',
                'Muehlenstraße 12',
                'Muenchen',
                '80238',
                3002
            ),
            (
                4012,
                'Ludwig.S@gmail.com',
                'Ludwig Stockmann',
                (1999, 6, 6),
                '01763433332',
                'Bernauerstrasse 34',
                'Muenchen',
                '80238',
                3002
            ),
            (
                4013,
                'tick.d@gmx.com',
                'Tick Duck',
                (1986, 9, 13),
                '01459275903',
                'Herzbergstrasse 25',
                'Hamburg',
                '34264',
                3003
            ),
            (
                4014,
                'trick.d@gmx.com',
                'Trick Duck',
                (1987, 5, 15),
                '01763463458',
                'Schönhauser Allee 45',
                'Hamburg',
                '34264',
                3003
            ),
            (
                4015,
                'track.d@gmx.com',
                'Track Duck',
                (1988, 7, 23),
                '01763423732',
                'Holzhauser Strasse 56',
                'Hamburg',
                '34264',
                3003
            ),
            (
                4016,
                'Siva.F@gmx.com',
                'Siva Franz',
                (1995, 5, 15),
                '01763445892',
                'Nollendorfstrasse 37',
                'Muenchen',
                '80238',
                3002
            ),
            (
                4017,
                'Luise.K@hotmail.com',
                'Luise Kieselbach',
                (1997, 8, 15),
                '01456423732',
                'Winterfeldstrasse 3',
                'Muenchen',
                '80238',
                3002
            ),
            (
                4018,
                'Linda.Ku@outlook.com',
                'Linda Kurz',
                (1981, 11, 11),
                '01763424962',
                'Goethestrasse 52',
                'Muenchen',
                '80238',
                3002
            ),
            (
                4019,
                'Hans.H@outlook.com',
                'Hans Helfer',
                (1995, 12, 11),
                '01276423732',
                'Pestalozzistrasse 72',
                'Muenchen',
                '80238',
                3002
            ),
            (
                4020,
                'Lucas.p@outlook.com',
                'Lucas Peeter',
                (1997, 2, 10),
                '01763434232',
                'Röntgenstrasse 75',
                'Muenchen',
                '80238',
                3002
            ),
            (
                4021,
                'Gabriel.P@gmail.com',
                'Gabriel Pfeifer',
                (1998, 10, 11),
                '01763462872',
                'Schlüterstrasse 45',
                'Hamburg',
                '34264',
                3001
            ),
            (
                4022,
                'Herbert.Graf@gmx.com',
                'Herbert Graf',
                (1994, 4, 17),
                '01265423732',
                'Fraunhoferstrasse 62',
                'Hamburg',
                '34264',
                3001
            ),
            (
                4023,
                'ali.cia@gmx.com',
                'Alicia Dreier',
                (1995, 12, 20),
                '01760086732',
                'EInsteinstrasse 49',
                'Hamburg',
                '34264',
                3001
            ),
            (
                4024,
                'Petunia@gmx.com',
                'Petunia Schreiber',
                (1995, 8, 15),
                '01768865732',
                'Arcostrasse 63',
                'Hamburg',
                '34264',
                3001
            ),
            (
                4025,
                'Horti23@gmx.com',
                'Hortensia Lutz',
                (1998, 1, 15),
                '01729963732',
                'Minnewitstrasse 66',
                'Hamburg',
                '34264',
                3001
            ),
            (
                4026,
                'Thomas.d@gmail.com',
                'Thomas Dach',
                (1989, 12, 19),
                '01755673732',
                'Pariser Strasse 37',
                'Muenchen',
                '80238',
                3002
            ),
            (
                4027,
                'Albert.g@outlook.com',
                'Albert Greif',
                (1995, 4, 19),
                '01762277732',
                'Güntzelstrasse 34',
                'Muenchen',
                '80238',
                3002
            ),
            (
                4028,
                'Tina.Z78@gmail.com',
                'Tina Ziegenbart',
                (1996, 6, 27),
                '01733983732',
                'Haberlstrasse 78',
                'Muenchen',
                '80238',
                3002
            ),
            (
                4029,
                'Anna.i@outlook.com',
                'Anna Igel',
                (1998, 2, 13),
                '01763433332',
                'Grainauer Strasse 56',
                'Muenchen',
                '80238',
                3002
            ),
            (
                4030,
                'Karl.M@gmail.com',
                'Karl Marx',
                (2000, 9, 23),
                '01752964732',
                'Eisenacher Strasse 98',
                'Muenchen',
                '80238',
                3002
            )
        ]
        for user in users:
            AddMethods.add_user(user)

        clients = [
            (
                5001,  # id
                (2018, 7, 12),  # created_on
                (2018, 8, 28, 21, 3, 0, 0),  # last_edited
                'Bibi Aisha',  # name
                'auf Flucht von Ehemann getrennt worden',  # note
                '01793456542',  # phone number
                (1990, 5, 1),  # birthday
                2002  # origin country id
            ),
            (
                5002,
                (2017, 3, 17),
                (2017, 12, 24, 12, 2, 0, 0),
                'Mustafa Kubi',
                'möchte eine Ausbildung beginnen',
                '01456378963',
                (1998, 12, 3),
                2002
            ),
            (
                5003,
                (2018, 1, 1),
                (2018, 3, 3, 14, 5, 0, 0),
                'Ali Baba',
                'fragt wie er seine deutsche Freundin heiraten kann',
                '01345626534',
                (1985, 6, 27),
                2002
            ),
            (
                5004,
                (2018, 8, 1),
                (2018, 8, 2, 16, 3, 0, 0),
                'Kamila Iman',
                'möchte zu ihrer Schwester in eine andere Aufnahmeeinrichtung ziehen',
                '01562736778',
                (1956, 4, 3),
                2002
            ),
            (
                5005,
                (2017, 9, 10),
                (2017, 10, 2, 15, 3, 0, 0),
                'Junis Haddad',
                'Informationen zum Asylverfahren',
                '013345736778',
                (1998, 6, 2),
                2006
            ),
            (
                5006,
                (2017, 9, 10),
                (2018, 9, 2, 16, 3, 0, 0),
                'Nael Mousa',
                'Informationen zum Asylverfahren',
                '01444436778',
                (1997, 6, 4),
                2006
            ),
            (
                5007,
                (2017, 9, 10),
                (2018, 1, 12, 16, 3, 0, 0),
                'Amir Hamdan',
                'Informationen zum Asylverfahren',
                '01457636778',
                (1996, 6, 8),
                2006
            ),
            (
                5008,
                (2017, 9, 10),
                (2018, 1, 2, 16, 3, 0, 0),
                'Amar Yousef',
                'Informationen zum Asylverfahren',
                '01566546778',
                (1995, 5, 10),
                2006
            ),
            (
                5009,
                (2017, 9, 10),
                (2017, 12, 2, 16, 3, 0, 0),
                'Tarek Habib',
                'Informationen zum Asylverfahren',
                '013564736778',
                (1994, 5, 12),
                2006
            ),
            (
                5010,
                (2017, 9, 10),
                (2018, 10, 2, 16, 3, 0, 0),
                'Kaya Yousif',
                'Informationen zum Asylverfahren',
                '01564586778',
                (1993, 4, 14),
                2006
            ),
            (
                5011,
                (2018, 4, 20),
                (2018, 5, 12, 16, 3, 0, 0),
                'Ilias Essa',
                'Familiennachzug',
                '01546536778',
                (1992, 3, 16),
                2007
            ),
            (
                5012,
                (2018, 4, 20),
                (2018, 5, 13, 16, 3, 0, 0),
                'Yasin Naffar',
                'Familiennachzug',
                '015345676778',
                (1991, 2, 18),
                2008
            ),
            (
                5013,
                (2018, 4, 20),
                (2018, 5, 12, 16, 3, 0, 0),
                'Mara Shaheen',
                'Familiennachzug',
                '015627334575',
                (1990, 1, 20),
                2007
            ),
            (
                5014,
                (2018, 4, 20),
                (2018, 5, 12, 16, 3, 0, 0),
                'Aleyna Alam',
                'Familiennachzug',
                '01865736778',
                (1989, 11, 22),
                2008
            ),
            (
                5015,
                (2018, 4, 20),
                (2018, 5, 2, 16, 3, 0, 0),
                'Yara Mansoor',
                'Familiennachzug',
                '01566666778',
                (1988, 11, 3),
                2007
            ),
            (
                5016,
                (2018, 4, 20),
                (2018, 10, 22, 16, 3, 0, 0),
                'Mayla Sulayman',
                'Familiennachzug',
                '01222736778',
                (1985, 12, 5),
                2008
            ),
            (
                5017,
                (2018, 4, 20),
                (2018, 8, 23, 16, 3, 0, 0),
                'Leyla Amin',
                'drohende Dublin-Abschiebung',
                '01555536778',
                (1987, 12, 7),
                2007
            ),
            (
                5018,
                (2018, 4, 20),
                (2018, 8, 22, 17, 3, 0, 0),
                'Amira Mustafa',
                'drohende Dublin-Abschiebung',
                '01563336778',
                (1985, 1, 9),
                2008
            ),
            (
                5019,
                (2018, 4, 20),
                (2018, 9, 2, 16, 3, 0, 0),
                'Kiano Isa',
                'drohende Dublin-Abschiebung',
                '01564566778',
                (1984, 1, 11),
                2007
            ),
            (
                5020,
                (2018, 4, 20),
                (2018, 8, 12, 17, 3, 0, 0),
                'Rafiki Omer',
                'drohende Dublin-Abschiebung',
                '01564657878',
                (1983, 1, 13),
                2008
            ),
            (
                5021,
                (2018, 12, 30),
                (2018, 12, 30, 12, 3, 0, 0),
                'Taio Aziz',
                'drohende Dublin-Abschiebung',
                '0154547688',
                (1982, 3, 30),
                2009
            ),
            (
                5022,
                (2018, 12, 30),
                (2018, 12, 30, 16, 3, 0, 0),
                'Nio Salih',
                'drohende Dublin-Abschiebung',
                '01564536778',
                (1981, 3, 14),
                2009
            ),
            (
                5023,
                (2018, 12, 30),
                (2018, 12, 30, 13, 4, 0, 0),
                'Chi Salah',
                'drohende Dublin-Abschiebung',
                '01565656778',
                (1980, 3, 28),
                2009
            ),
            (
                5024,
                (2018, 12, 30),
                (2018, 12, 30, 18, 3, 0, 0),
                'Zola Hamid',
                'drohende Dublin-Abschiebung',
                '01232336778',
                (1978, 3, 26),
                2009
            ),
            (
                5025,
                (2018, 12, 30),
                (2018, 12, 30, 16, 3, 0, 0),
                'Malaika Hussain',
                'möchte heiraten',
                '01562277678',
                (1976, 4, 24),
                2009
            ),
            (
                5026,
                (2018, 12, 30),
                (2018, 12, 30, 17, 5, 0, 0),
                'Jala Hana',
                'möchte heiraten',
                '01388736778',
                (1975, 4, 23),
                2010
            ),
            (
                5027,
                (2018, 12, 30),
                (2018, 12, 30, 16, 3, 0, 0),
                'Imani Naser',
                'möchte heiraten',
                '01367836778',
                (1974, 6, 21),
                2010
            ),
            (
                5028,
                (2018, 12, 30),
                (2018, 12, 30, 18, 3, 0, 0),
                'Ashanti Abba',
                'möchte heiraten',
                '01564466678',
                (1972, 6, 19),
                2010
            ),
            (
                5029,
                (2018, 12, 30),
                (2018, 12, 30, 17, 3, 0, 0),
                'Saba Ibraheem',
                'möchte heiraten',
                '01534636778',
                (1970, 6, 17),
                2010
            ),
            (
                5030,
                (2018, 2, 12),
                (2018, 12, 2, 12, 3, 0, 0),
                'Baschar Abneh',
                'möchte heiraten',
                '01562778978',
                (1961, 6, 15),
                2010
            ),
            (
                5031,
                (2018, 2, 12),
                (2018, 8, 12, 13, 3, 0, 0),
                'Djamal Abdulah',
                'möchte Unterkunft wechseln',
                '01534536778',
                (1960, 7, 13),
                2003
            ),
            (
                5032,
                (2018, 2, 12),
                (2018, 8, 5, 16, 3, 0, 0),
                'Firas Abdel',
                'möchte Unterkunft wechseln',
                '01568564778',
                (1959, 7, 11),
                2003
            ),
            (
                5033,
                (2018, 2, 12),
                (2018, 4, 2, 12, 3, 0, 0),
                'Jalil Karim',
                'möchte Unterkunft wechseln',
                '01864636778',
                (1958, 8, 9),
                2003
            ),
            (
                5034,
                (2018, 2, 12),
                (2018, 3, 8, 12, 3, 0, 0),
                'Najiim Ali',
                'Namensberichtigung',
                '01562456778',
                (1957, 8, 7),
                2003
            ),
            (
                5035,
                (2018, 2, 12),
                (2018, 3, 2, 15, 3, 0, 0),
                'Enis Sam',
                'Namensberichtigung',
                '01222736778',
                (1956, 9, 12),
                2003
            ),
            (
                5036,
                (2018, 11, 13),
                (2018, 11, 13, 18, 3, 0, 0),
                'Gibran Hadad',
                'Namensberichtigung',
                '01526478978',
                (1955, 9, 14),
                2004
            ),
            (
                5037,
                (2018, 11, 13),
                (2018, 11, 15, 16, 3, 0, 0),
                'Esat Hasan',
                'Fragen zu Ausbildungsduldung',
                '01563333778',
                (1954, 10, 16),
                2004
            ),
            (
                5038,
                (2018, 11, 13),
                (2018, 11, 14, 12, 2, 0, 0),
                'Leron Rahman',
                'Fragen zu Ausbildungsduldung',
                '01563487778',
                (1953, 10, 18),
                2004
            ),
            (
                5039,
                (2018, 11, 13),
                (2018, 12, 2, 7, 13, 0, 0),
                'Saad Ahmed',
                'Fragen zu Ausbildungsduldung',
                '01562723678',
                (1952, 11, 20),
                2004
            ),
            (
                5040,
                (2018, 11, 13),
                (2018, 11, 13, 13, 3, 0, 0),
                'Zarif Rashid',
                'Fragen zu Ausbildungsduldung',
                '01533336778',
                (1951, 12, 22),
                2004
            ),
        ]
        for client in clients:
            AddMethods.add_client(client)

        records = [
            (
                7001,  # id
                4001,  # creator id
                3003,  # rlc id
                (2018, 7, 12),  # created
                (2018, 8, 29, 13, 54, 0, 0),  # las edited
                5001,  # client
                (2018, 7, 10),  # first contact
                (2018, 8, 14, 17, 30, 0, 0),  # last contact
                'AZ-123/18',  # record token
                'cl',  # status, cl wa op
                [4001],  # working on
                [1001, 1002]  # tags
            ), (
                7002,
                4004,
                3003,
                (2018, 6, 23),
                (2018, 8, 22, 23, 3, 0, 0),
                5002,
                (2018, 6, 20),
                (2018, 7, 10, 17, 30, 0, 0),
                'AZ-124/18',
                'op',
                [4004, 4001],
                [1003, 1004]
            ), (
                7003,
                4005,
                3003,
                (2018, 8, 24),
                (2018, 8, 31, 1, 2, 0, 0),
                5003,
                (2018, 8, 22),
                (2018, 8, 22, 18, 30, 0, 0),
                'AZ-125/18',
                'wa',
                [4003, 4001],
                [1001, 1004]
            ), (
                7004,
                4001,
                3003,
                (2018, 3, 10),
                (2018, 4, 30, 19, 22, 0, 0),
                5004,
                (2018, 3, 9),
                (2018, 3, 24, 15, 54, 0, 0),
                'AZ-126/18',
                'cl',
                [4001, 4004],
                [1005, 1001]
            ), (
                7005,
                4001,
                3003,
                (2017, 9, 10),
                (2017, 10, 2, 15, 3, 0, 0),
                5005,
                (2017, 9, 10),
                (2017, 10, 2, 15, 3, 0, 0),
                'AZ-127/18',
                'cl',
                [4001, 4004],
                [1005, 1001]
            ), (
                7006,
                4002,
                3001,
                (2017, 9, 10),
                (2018, 9, 2, 16, 3, 0, 0),
                5006,
                (2017, 9, 10),
                (2018, 9, 2, 16, 3, 0, 0),
                'AZ-128/18',
                'wa',
                [4002, 4004],
                [1005, 1001]
            ), (
                7007,
                4003,
                3001,
                (2017, 9, 10),
                (2018, 1, 12, 16, 3, 0, 0),
                5007,
                (2017, 9, 10),
                (2018, 1, 12, 16, 3, 0, 0),
                'AZ-129/18',
                'op',
                [4003, 4004],
                [1005, 1001]
            ), (
                7008,
                4004,
                3003,
                (2017, 9, 10),
                (2018, 1, 2, 16, 3, 0, 0),
                5008,
                (2017, 9, 10),
                (2018, 1, 2, 16, 3, 0, 0),
                'AZ-130/18',
                'cl',
                [4005, 4004],
                [1004, 1001]
            ), (
                7009,
                4005,
                3003,
                (2017, 9, 10),
                (2018, 12, 2, 16, 3, 0, 0),
                5009,
                (2017, 9, 10),
                (2018, 12, 2, 16, 3, 0, 0),
                'AZ-131/18',
                'wa',
                [4005, 4004],
                [1005, 1003]
            ), (
                7010,
                4006,
                3002,
                (2017, 9, 10),
                (2018, 10, 2, 16, 3, 0, 0),
                5010,
                (2017, 9, 10),
                (2018, 10, 2, 16, 3, 0, 0),
                'AZ-132/18',
                'op',
                [4006, 4004],
                [1002, 1001]
            ), (
                7011,
                4007,
                3002,
                (2018, 4, 20),
                (2018, 5, 12, 16, 3, 0, 0),
                5011,
                (2018, 4, 20),
                (2018, 5, 12, 16, 3, 0, 0),
                'AZ-133/18',
                'cl',
                [4005, 4007],
                [1005, 1004]
            ), (
                7012,
                4008,
                3003,
                (2018, 4, 20),
                (2018, 5, 13, 16, 3, 0, 0),
                5012,
                (2018, 4, 20),
                (2018, 5, 13, 16, 3, 0, 0),
                'AZ-134/18',
                'cl',
                [4008, 4004],
                [1003, 1001]
            ), (
                7013,
                4008,
                3003,
                (2018, 4, 20),
                (2018, 5, 12, 16, 3, 0, 0),
                5013,
                (2018, 4, 20),
                (2018, 5, 12, 16, 3, 0, 0),
                'AZ-135/18',
                'wa',
                [4005, 4008],
                [1005, 1001]
            ), (
                7014,
                4008,
                3003,
                (2018, 4, 20),
                (2018, 5, 12, 16, 3, 0, 0),
                5014,
                (2018, 4, 20),
                (2018, 5, 12, 16, 3, 0, 0),
                'AZ-136/18',
                'wa',
                [4008, 4004],
                [1005, 1001]
            ), (
                7015,
                4009,
                3001,
                (2018, 4, 20),
                (2018, 5, 2, 16, 3, 0, 0),
                5015,
                (2018, 4, 20),
                (2018, 5, 2, 16, 3, 0, 0),
                'AZ-137/18',
                'cl',
                [4005, 4009],
                [1005, 1001]
            ), (
                7016,
                4010,
                3001,
                (2018, 4, 20),
                (2018, 10, 22, 16, 3, 0, 0),
                5016,
                (2018, 4, 20),
                (2018, 10, 22, 16, 3, 0, 0),
                'AZ-138/18',
                'cl',
                [4005, 4010],
                [1005, 1001]
            ), (
                7017,
                4011,
                3002,
                (2018, 4, 20),
                (2018, 8, 23, 16, 3, 0, 0),
                5017,
                (2018, 4, 20),
                (2018, 8, 23, 16, 3, 0, 0),
                'AZ-139/18',
                'cl',
                [4011, 4004],
                [1005, 1001]
            ), (
                7018,
                4011,
                3002,
                (2018, 4, 20),
                (2018, 8, 22, 17, 3, 0, 0),
                5018,
                (2018, 4, 20),
                (2018, 8, 22, 17, 3, 0, 0),
                'AZ-140/18',
                'cl',
                [4011, 4004],
                [1005, 1001, 1003]
            ), (
                7019,
                4012,
                3002,
                (2018, 4, 20),
                (2018, 9, 2, 16, 3, 0, 0),
                5019,
                (2018, 4, 20),
                (2018, 9, 2, 16, 3, 0, 0),
                'AZ-141/18',
                'cl',
                [4012, 4004],
                [1005, 1003]
            ), (
                7020,
                4012,
                3002,
                (2018, 4, 20),
                (2018, 8, 12, 17, 3, 0, 0),
                5020,
                (2018, 4, 20),
                (2018, 8, 12, 17, 3, 0, 0),
                'AZ-142/18',
                'wa',
                [4012, 4004],
                [1005, 1001]
            ), (
                7021,
                4013,
                3003,
                (2018, 12, 30),
                (2018, 12, 30, 12, 3, 0, 0),
                5021,
                (2018, 12, 30),
                (2018, 12, 30, 12, 3, 0, 0),
                'AZ-143/18',
                'cl',
                [4013, 4004],
                [1005, 1001]
            ), (
                7022,
                4014,
                3003,
                (2018, 12, 30),
                (2018, 12, 30, 16, 3, 0, 0),
                5022,
                (2018, 12, 30),
                (2018, 12, 30, 16, 3, 0, 0),
                'AZ-144/18',
                'cl',
                [4005, 4014],
                [1005, 1001]
            ), (
                7023,
                4014,
                3003,
                (2018, 12, 30),
                (2018, 12, 30, 13, 4, 0, 0),
                5023,
                (2018, 12, 30),
                (2018, 12, 30, 13, 4, 0, 0),
                'AZ-145/18',
                'op',
                [4014, 4004],
                [1004, 1001]
            ), (
                7024,
                4015,
                3003,
                (2018, 12, 30),
                (2018, 12, 30, 18, 3, 0, 0),
                5024,
                (2018, 12, 30),
                (2018, 12, 30, 18, 3, 0, 0),
                'AZ-146/18',
                'op',
                [4005, 4015],
                [1005, 1003]
            ), (
                7025,
                4016,
                3002,
                (2018, 12, 30),
                (2018, 12, 30, 16, 3, 0, 0),
                5025,
                (2018, 12, 30),
                (2018, 12, 30, 16, 3, 0, 0),
                'AZ-147/18',
                'cl',
                [4016, 4004],
                [1004, 1001]
            ), (
                7026,
                4017,
                3002,
                (2018, 12, 30),
                (2018, 12, 30, 17, 5, 0, 0),
                5026,
                (2018, 12, 30),
                (2018, 12, 30, 17, 5, 0, 0),
                'AZ-148/18',
                'cl',
                [4005, 4017],
                [1005, 1001]
            ), (
                7027,
                4018,
                3002,
                (2018, 12, 30),
                (2018, 12, 30, 16, 3, 0, 0),
                5027,
                (2018, 12, 30),
                (2018, 12, 30, 16, 3, 0, 0),
                'AZ-149/18',
                'wa',
                [4018, 4004],
                [1005, 1001]
            ), (
                7028,
                4019,
                3002,
                (2018, 12, 30),
                (2018, 12, 30, 18, 3, 0, 0),
                5028,
                (2018, 12, 30),
                (2018, 12, 30, 18, 3, 0, 0),
                'AZ-150/18',
                'wa',
                [4005, 4019],
                [1005, 1003]
            ), (
                7029,
                4020,
                3002,
                (2018, 12, 30),
                (2018, 12, 30, 17, 3, 0, 0),
                5029,
                (2018, 12, 30),
                (2018, 12, 30, 17, 3, 0, 0),
                'AZ-151/18',
                'cl',
                [4020, 4004],
                [1005, 1001]
            ), (
                7030,
                4021,
                3001,
                (2018, 2, 12),
                (2018, 12, 2, 12, 3, 0, 0),
                5030,
                (2018, 2, 12),
                (2018, 12, 2, 12, 3, 0, 0),
                'AZ-152/18',
                'cl',
                [4005, 4021],
                [1004, 1001]
            ), (
                7031,
                4022,
                3001,
                (2018, 2, 12),
                (2018, 8, 12, 13, 3, 0, 0),
                5031,
                (2018, 2, 12),
                (2018, 8, 12, 13, 3, 0, 0),
                'AZ-153/18',
                'cl',
                [4022, 4004],
                [1005, 1001]
            ), (
                7032,
                4023,
                3001,
                (2018, 2, 12),
                (2018, 8, 5, 16, 3, 0, 0),
                5032,
                (2018, 2, 12),
                (2018, 8, 5, 16, 3, 0, 0),
                'AZ-154/18',
                'cl',
                [4005, 4023],
                [1005, 1003]
            ), (
                7033,
                4024,
                3001,
                (2018, 2, 12),
                (2018, 4, 2, 12, 3, 0, 0),
                5033,
                (2018, 2, 12),
                (2018, 4, 2, 12, 3, 0, 0),
                'AZ-155/18',
                'op',
                [4024, 4004],
                [1005, 1001]
            ), (
                7034,
                4025,
                3001,
                (2018, 2, 12),
                (2018, 3, 8, 12, 3, 0, 0),
                5034,
                (2018, 2, 12),
                (2018, 3, 8, 12, 3, 0, 0),
                'AZ-156/18',
                'op',
                [4005, 4025],
                [1004, 1001]
            ), (
                7035,
                4026,
                3002,
                (2018, 2, 12),
                (2018, 3, 2, 15, 3, 0, 0),
                5035,
                (2018, 2, 12),
                (2018, 3, 2, 15, 3, 0, 0),
                'AZ-157/18',
                'cl',
                [4026, 4004],
                [1005, 1002]
            ), (
                7036,
                4027,
                3002,
                (2018, 11, 13),
                (2018, 11, 13, 18, 3, 0, 0),
                5036,
                (2018, 11, 13),
                (2018, 11, 13, 18, 3, 0, 0),
                'AZ-158/18',
                'cl',
                [4005, 4027],
                [1005, 1001]
            ), (
                7037,
                4028,
                3002,
                (2018, 11, 13),
                (2018, 11, 15, 16, 3, 0, 0),
                5037,
                (2018, 11, 13),
                (2018, 11, 15, 16, 3, 0, 0),
                'AZ-159/18',
                'op',
                [4005, 4028],
                [1003, 1001]
            ), (
                7038,
                4029,
                3002,
                (2018, 11, 13),
                (2018, 11, 14, 12, 2, 0, 0),
                5038,
                (2018, 11, 13),
                (2018, 11, 14, 12, 2, 0, 0),
                'AZ-160/18',
                'wa',
                [4029, 4004],
                [1005, 1001]
            ), (
                7039,
                4030,
                3002,
                (2018, 11, 13),
                (2018, 12, 2, 7, 13, 0, 0),
                5039,
                (2018, 11, 13),
                (2018, 12, 2, 7, 13, 0, 0),
                'AZ-161/18',
                'cl',
                [4030, 4004],
                [1005, 1002]
            ), (
                7040,
                4030,
                3002,
                (2018, 11, 13),
                (2018, 11, 13, 13, 3, 0, 0),
                5040,
                (2018, 11, 13),
                (2018, 11, 13, 13, 3, 0, 0),
                'AZ-162/18',
                'cl',
                [4030, 4004],
                [1005, 1001]
            )]
        for record in records:
            AddMethods.add_record(record)

        groups = [
            (
                6001,
                4002,  # id des Nutzers der die Gruppe erstellt hat
                3001,  # id der RLC zu der die Gruppe gehoert
                'RLC Hamburg Bucerius Law School members',  # name der Gruppe
                False,  # gibt an ob die Gruppe fuer alle sichtbar ist
                [4002, 4003]  # IDs aller Nutzer die in der Gruppe sind
            ),
            (
                6002,
                4001,
                3003,
                'RLC München member',
                False,
                [4001, 4004]
            ),
            (
                6003,
                4001,
                3003,
                'RLC München board_member',
                False,
                [4001]
            )
        ]
        for group in groups:
            AddMethods.add_group(group)


class AddMethods:
    @staticmethod
    def add_user(user):
        """
		creates a user in database with provided values
		Args:
			user: (email [string], name [string], is_superuser [bool], password [string]) or
				(id [number], email [string], name [string], is_superuser [bool], password [string])

		Returns:

		"""

        if user.__len__() == 4:
            us = UserProfile(email=user[0], name=user[1], is_superuser=user[2], is_active=True)
            us.set_password(user[3])
        elif user.__len__() == 5:
            us = UserProfile(id=user[0], email=user[1], name=user[2], is_superuser=user[3], is_active=True)
            us.set_password(user[4])
        elif user.__len__() == 9:
            us = UserProfile(id=user[0], email=user[1], name=user[2], phone_number=user[4],
                             street=user[5], city=user[6], postal_code=user[7], rlc_id=user[8])
            us.birthday = AddMethods.generate_date(user[3])
            us.set_password('qwe123')
            us.save()
        else:
            raise AttributeError

    @staticmethod
    def add_rlc(rlc):
        """
		creates rlc in database with provided values
		Args:
			rlc: (name [String], uni_tied [bool], part_of_umbrella [bool]) or
				(id[number], name [String], uni_tied [bool], part_of_umbrella [bool])

		Returns:

		"""
        if rlc.__len__() == 3:
            lc = Rlc(name=rlc[0], uni_tied=rlc[1], part_of_umbrella=rlc[2])
        elif rlc.__len__() == 4:
            lc = Rlc(id=rlc[0], name=rlc[1], uni_tied=rlc[2], part_of_umbrella=rlc[3])
        elif rlc.__len__() == 5:
            lc = Rlc(id=rlc[0], name=rlc[1], uni_tied=rlc[2], part_of_umbrella=rlc[3], note=rlc[4])
        else:
            raise AttributeError
        lc.save()

    @staticmethod
    def add_permission(permission):
        """
		creates permissions in database
		Args:
			permission: (name of permission [String}) or
						(id [number], permissionName [String])

		Returns:

		"""
        if isinstance(permission, str):
            perm = Permission(name=permission)
        elif permission.__len__() == 1:
            perm = Permission(name=permission[0])
        elif permission.__len__() == 2:
            perm = Permission(id=permission[0], name=permission[1])
        else:
            raise AttributeError
        perm.save()

    @staticmethod
    def add_record_tag(tag):
        """
		creates tag in database
		Args:
			tag: (name of tag [String]) or
				(id [number], name [String])

		Returns:

		"""
        if tag.__len__() == 1:
            t = RecordTag(name=tag[0])
        elif tag.__len__() == 2:
            t = RecordTag(id=tag[0], name=tag[1])
        else:
            raise AttributeError
        t.save()

    @staticmethod
    def add_record_document_tag(tag):
        if tag.__len__() == 1:
            t = RecordDocumentTag(name=tag[0])
        elif tag.__len__() == 2:
            t = RecordDocumentTag(id=tag[0], name=tag[1])
        else:
            raise AttributeError
        t.save()

    @staticmethod
    def add_country(country):
        """
		creates OriginCountry in database with provided values
		Args:
			country: (name [String], state [string, length=2, compare to OriginCountry model) or
					(id [number], name [String], state [string, length=2, compare to OriginCountry model)
		Returns:

		"""
        if country.__len__() == 1:
            c = OriginCountry(name=country[0])
        elif country.__len__() == 2:
            c = OriginCountry(name=country[0], state=country[1])
        elif country.__len__() == 3:
            c = OriginCountry(id=country[0], name=country[1], state=country[2])
        else:
            raise AttributeError
        c.save()

    @staticmethod
    def add_to_rlc(user_id, rlc_id):
        """
        add the user with user_id as a member to the rlc with rlc_id
		Args:
			user_id: id of the user which will be added
			rlc_id: id of the rlc which will the user will be added  to

		Returns:

		"""
        rlc = Rlc.objects.get(pk=rlc_id)
        user = UserProfile.objects.get(pk=user_id)
        user.rlc = rlc
        user.save()

    @staticmethod
    def add_group(group, rlc_id=None):
        if not rlc_id:
            AddMethods.add_group_not_in_rlc(group)
        else:
            AddMethods.add_group_in_rlc(group, rlc_id)

    @staticmethod
    def add_group_in_rlc(group, rlc_id):
        if group.__len__() == 2:
            g = Group(name=group[0], visible=group[1], from_rlc_id=rlc_id)
        elif group.__len__() == 5:
            g = Group(id=group[0], creator_id=group[1], from_rlc_id=rlc_id, name=group[2], visible=group[3])
            g.save()
            for user_id in group[5]:
                g.group_members.add(UserProfile.objects.get(pk=user_id))
        else:
            raise AttributeError
        g.save()

    @staticmethod
    def add_group_not_in_rlc(group):
        if group.__len__() == 3:
            g = Group(name=group[0], visible=group[1], from_rlc_id=group[2])
        elif group.__len__() == 6:
            g = Group(id=group[0], creator_id=group[1], from_rlc_id=group[2], name=group[3], visible=group[4])
            g.save()
            for user_id in group[5]:
                g.group_members.add(UserProfile.objects.get(pk=user_id))
        else:
            raise AttributeError
        g.save()

    @staticmethod
    def add_client(client):
        if client.__len__() == 8:
            cl = Client(id=client[0], name=client[3], note=client[4], phone_number=client[5],
                        origin_country_id=client[7])
            cl.created_on = AddMethods.generate_date(client[1])
            cl.last_edited = AddMethods.generate_datetime(client[2])
            cl.birthday = AddMethods.generate_date(client[6])
            cl.save()

    @staticmethod
    def add_record(record):
        if record.__len__() == 12:
            rc = Record(id=record[0], creator_id=record[1], from_rlc_id=record[2], client_id=record[5],
                        record_token=record[8], state=record[9])
            rc.created_on = AddMethods.generate_date(record[3])
            rc.last_edited = AddMethods.generate_datetime(record[4])
            rc.first_contact_date = AddMethods.generate_date(record[6])
            rc.last_contact_date = AddMethods.generate_datetime(record[7])
            rc.save()
            for user_id in record[10]:
                rc.working_on_record.add(UserProfile.objects.get(pk=user_id))
            for tag_id in record[11]:
                rc.tagged.add(RecordTag.objects.get(pk=tag_id))
            rc.save()

    @staticmethod
    def generate_date(information):
        return datetime(information[0], information[1], information[2]).replace(
            tzinfo=pytz.timezone(settings.TIME_ZONE))

    @staticmethod
    def generate_datetime(information):
        return datetime(information[0], information[1], information[2], information[3], information[4], information[5],
                        information[6]).replace(
            tzinfo=pytz.timezone(settings.TIME_ZONE))
