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

from datetime import datetime

import pytz
from django.conf import settings

from backend.api.models import *
from backend.recordmanagement.models import (
    OriginCountry,
    RecordDocumentTag,
    RecordTag,
)
from backend.static.permissions import get_all_permissions_strings
from backend.files.models import FolderPermission
from backend.files.static.folder_permissions import get_all_folder_permissions_strings


class Fixtures:
    @staticmethod
    def create_example_static_users():
        user = UserProfile(id=1, email="abc@web.de", name="Betsy", is_active=True)
        user.set_password("qwe123")
        user.save()

        user = UserProfile(
            id=2, email="jehob@web.de", name="Peter", is_active=True, is_superuser=True
        )
        user.set_password("qwe123")
        user.save()

    @staticmethod
    def create_example_record_tags():
        tags = [
            ("Dublin III",),
            ("family reunion",),
            ("asylum",),
            ("stay",),
            ("employment",),
        ]
        for single_tag in tags:
            AddMethods.add_record_tag(single_tag)

    @staticmethod
    def create_example_origin_countries():
        countries = [
            ("Botswana", "st"),
            ("Ghana", "ot"),
            ("Nigeria", "so"),
            ("Turkey", "so"),
            ("Sahara", "ot"),
            ("Ukraine", "st"),
            ("Syria", "ot"),
        ]
        for country in countries:
            AddMethods.add_country(country)

    @staticmethod
    def create_real_origin_countries():
        countries = [
            ("Abchasien",),
            ("Afghanistan",),
            ("Ägypten",),
            ("Albanien",),
            ("Algerien",),
            ("Andorra",),
            ("Angola",),
            ("Antigua und Barbuda",),
            ("Äquatorialguinea",),
            ("Argentinien",),
            ("Armenien",),
            ("Arzach",),
            ("Aserbaidschan",),
            ("Äthiopien",),
            ("Australien",),
            ("Bahamas",),
            ("Bahrain",),
            ("Bangladesch",),
            ("Barbados",),
            ("Belgien",),
            ("Belize",),
            ("Benin",),
            ("Bhutan",),
            ("Bolivien",),
            ("Bosnien und Herzegowina",),
            ("Botswana",),
            ("Brasilien",),
            ("Brunei",),
            ("Bulgarien",),
            ("Burkina Faso",),
            ("Burundi",),
            ("Chile",),
            ("Republik China",),
            ("Volksrepublik China",),
            ("Cookinseln",),
            ("Costa Rica",),
            ("Dänemark",),
            ("Deutschland",),
            ("Dominica",),
            ("Dominikanische Republik",),
            ("Dschibuti",),
            ("Ecuador",),
            ("El Salvador",),
            ("Elfenbeinküste",),
            ("Eritrea",),
            ("Estland",),
            ("Fidschi",),
            ("Finnland",),
            ("Frankreich",),
            ("Gabun",),
            ("Gambia",),
            ("Georgien",),
            ("Ghana",),
            ("Grenada",),
            ("Griechenland",),
            ("Guatemala",),
            ("Guinea",),
            ("Guinea-Bissau",),
            ("Guyana",),
            ("Haiti",),
            ("Honduras",),
            ("Indien",),
            ("Indonesien",),
            ("Irak",),
            ("Iran",),
            ("Irland",),
            ("Island",),
            ("Israel",),
            ("Italien",),
            ("Jamaika",),
            ("Japan",),
            ("Jemen",),
            ("Jordanien",),
            ("Kambodscha",),
            ("Kamerun",),
            ("Kanada",),
            ("Kap Verde",),
            ("Kasachstan",),
            ("Katar",),
            ("Kenia",),
            ("Kirgisistan",),
            ("Kiribati",),
            ("Kolumbien",),
            ("Komoren",),
            ("Kongo, Demokratische Republik",),
            ("Kongo, Republik",),
            ("Nordkorea",),
            ("Südkorea",),
            ("Kosovo",),
            ("Kroatien",),
            ("Kuba",),
            ("Kuwait",),
            ("Laos",),
            ("Lesotho",),
            ("Lettland",),
            ("Libanon",),
            ("Liberia",),
            ("Libyen",),
            ("Liechtenstein",),
            ("Litauen",),
            ("Luxemburg",),
            ("Madagaskar",),
            ("Malawi",),
            ("Malaysia",),
            ("Malediven",),
            ("Mali",),
            ("Malta",),
            ("Marokko",),
            ("Marshallinseln",),
            ("Mauretanien",),
            ("Mauritius",),
            ("Mexiko",),
            ("Mikronesien",),
            ("Moldau",),
            ("Monaco",),
            ("Mongolei",),
            ("Montenegro",),
            ("Mosambik",),
            ("Myanmar",),
            ("Namibia",),
            ("Nauru",),
            ("Nepal",),
            ("Neuseeland",),
            ("Nicaragua",),
            ("Niederlande",),
            ("Curaçao",),
            ("Sint Maarten",),
            ("Niger",),
            ("Nigeria",),
            ("Niue",),
            ("Nordmazedonien",),
            ("Nordzypern",),
            ("Norwegen",),
            ("Oman",),
            ("Österreich",),
            ("Osttimor / Timor-Leste",),
            ("Pakistan",),
            ("Palästina",),
            ("Palau",),
            ("Panama",),
            ("Papua-Neuguinea",),
            ("Paraguay",),
            ("Peru",),
            ("Philippinen",),
            ("Polen",),
            ("Portugal",),
            ("Ruanda",),
            ("Rumänien",),
            ("Russland",),
            ("Salomonen",),
            ("Sambia",),
            ("Samoa",),
            ("San Marino",),
            ("São Tomé und Príncipe",),
            ("Saudi-Arabien",),
            ("Schweden",),
            ("Schweiz",),
            ("Senegal",),
            ("Serbien",),
            ("Seychellen",),
            ("Sierra Leone",),
            ("Simbabwe",),
            ("Singapur",),
            ("Slowakei",),
            ("Slowenien",),
            ("Somalia",),
            ("Somaliland",),
            ("Spanien",),
            ("Sri Lanka",),
            ("St. Kitts und Nevis",),
            ("St. Lucia",),
            ("St. Vincent und die Grenadinen",),
            ("Südafrika",),
            ("Sudan ",),
            ("Südossetien",),
            ("Südsudan",),
            ("Suriname",),
            ("Swasiland",),
            ("Syrien",),
            ("Tadschikistan",),
            ("Tansania",),
            ("Thailand",),
            ("Togo",),
            ("Tonga",),
            ("Transnistrien",),
            ("Trinidad und Tobago",),
            ("Tschad",),
            ("Tschechien",),
            ("Tunesien",),
            ("Türkei",),
            ("Turkmenistan",),
            ("Tuvalu",),
            ("Uganda",),
            ("Ukraine",),
            ("Ungarn",),
            ("Uruguay",),
            ("Usbekistan",),
            ("Vanuatu",),
            ("Vatikanstadt",),
            ("Venezuela",),
            ("Vereinigte Arabische Emirate",),
            ("Vereinigte Staaten",),
            ("Vereinigtes Königreich",),
            ("Vietnam",),
            ("Weißrussland",),
            ("Westsahara",),
            ("Zentral­afrikanische Republik",),
            ("Zypern",),
            ("unbekanntes Herkunftsland",),
        ]
        for country in countries:
            AddMethods.add_country(country)

    @staticmethod
    def create_example_permissions():
        permissions = [
            ("add_records",),
            ("edit_records",),
            ("remove_records",),
            ("view_records",),
            ("view_users",),
            ("view_records_full_detail",),
            ("can_consult",),
        ]
        real_perms = get_all_permissions_strings()
        for rperm in real_perms:
            if (rperm,) not in permissions:
                permissions.append((rperm,))

        for perm in permissions:
            AddMethods.add_permission(perm)

    @staticmethod
    def create_rlcs():
        rlcs = (
            (1, "RLC Muenchen", False, True),
            (2, "RLC Hamburg", False, True),
            (3, "RLC Leipzig", False, True),
        )
        for rlc in rlcs:
            AddMethods.add_rlc(rlc)

    @staticmethod
    def create_real_permissions():
        permissions = get_all_permissions_strings()
        for permission in permissions:
            AddMethods.add_permission(permission)

    @staticmethod
    def create_real_permissions_no_duplicates():
        permissions = get_all_permissions_strings()
        for permission in permissions:
            if Permission.objects.filter(name=permission).count() == 0:
                AddMethods.add_permission(permission)

    @staticmethod
    def create_real_folder_permissions_no_duplicate():
        folder_permissions = get_all_folder_permissions_strings()
        for folder_permission in folder_permissions:
            if FolderPermission.objects.filter(name=folder_permission).count() == 0:
                AddMethods.add_folder_permission(folder_permission)

    @staticmethod
    def create_real_tags():
        tags = [
            ("Familiennachzug",),
            ("Dublin IV",),
            ("Arbeitserlaubnis",),
            ("Flüchtlingseigenschaft",),
            ("subsidiärer Schutz",),
            ("Eheschließung",),
            ("Verlobung",),
            ("illegale Ausreise aus dem Bundesgebiet",),
            ("Untertauchen",),
            ("Kinder anerkennen",),
            ("Ausbildung",),
            ("Geburt ",),
            ("Eines Kindes im Asylverfahren",),
            ("Duldung",),
            ("Ausbildungsduldung",),
            ("Visum",),
            ("Anhörung",),
            ("Wechsel der Unterkunft",),
            ("Wohnsitzauflage",),
            ("Folgeantrag",),
            ("Zweitantrag",),
            ("Unterbringung im Asylverfahren",),
            ("Widerruf der Asylberechtigung",),
            ("Rücknahme der Asyberechtigung",),
            ("Passbeschaffung",),
            ("Mitwirkungspflichten",),
            ("Nichtbetreiben des Verfahrens",),
            ("Krankheit im Asylverfahren",),
            ("Familienasyl",),
            ("UmF",),
            ("Familienzusammenführung nach Dublin III",),
            ("Negativbescheid",),
            ("Relocation",),
            ("Resettlement",),
            ("Asylbewerberleistungsgesetz",),
            ("Kirchenasyl",),
            ("Asylantrag",),
            ("Abschiebung",),
            ("Untätigkeitsklage",),
            ("Studium",),
            ("Strafverfolgung",),
            ("Sonstiges",),
            ("Aufenthaltserlaubnis",),
            ("Aufenthaltsgestattung",),
            ("Niederlassungserlaubnis",),
            ("Einbürgerung",),
            ("Staatsbürgerschaft",),
        ]
        for tag in tags:
            AddMethods.add_record_tag(tag)

    @staticmethod
    def create_real_document_tags():
        tags = [
            ("Pass",),
            ("Passersatzpapier",),
            ("Geburtsurkunde",),
            ("Heiratsurkunde",),
            ("Ankunftsnachweis",),
            ("Duldung",),
            ("Aufenthaltsgestattung",),
            ("Aufenthaltstitel",),
            ("Bescheid (Ablehnung)",),
            ("Bescheid (Flüchtling)",),
            ("Bescheid (subsidiärer Schutz)",),
            ("Bescheid (Abschiebeverbote)",),
            ("Bescheid (Sozialleistungen)",),
            ("Bescheid (Arbeiten)",),
            ("Bescheid (Wohnen)",),
            ("Widerspruch",),
            ("Antwortschreiben",),
            ("Erwiderung",),
            ("Sachstandsanfrage",),
            ("Klageschrift",),
            ("Akteneinsicht",),
            ("Anfrage",),
            ("Terminvereinbarung",),
            ("Attest",),
            ("Verschwiegenheitserklärung",),
            ("Datenschutzerklärung",),
            ("Erklärung",),
            ("Vertrag",),
            ("Antrag",),
            ("Zeugnis",),
            ("Zertifikat",),
            ("Vollmacht",),
            ("Anhörungsvorbereitung",),
            ("Haftbeschluss",),
            ("Anzeige",),
            ("Strafanzeige",),
            ("Medizinischer Befund",),
            ("Haftantrag",),
            ("Haftaufhebung",),
            ("Haftbeschwerde",),
            ("Antwort an",),
            ("Amtsgericht",),
            ("Anwältin/Anwalt",),
            ("Beratungsstelle",),
            ("Korrespondenz",),
            ("Supervisor*in",),
            ("Dolmetscher*in",),
            ("Sonstiges",),
            ("Antwort von",),
            ("Verwaltungsgericht",),
        ]
        for tag in tags:
            AddMethods.add_record_document_tag(tag)

    @staticmethod
    def create_real_starting_rlcs():
        rlcs = (("RLC München", False, True), ("RLC Hamburg", False, True))
        for rlc in rlcs:
            AddMethods.add_rlc(rlc)
        return list(Rlc.objects.all())

    @staticmethod
    def create_real_groups(rlcs):
        groups = [("Members", False), ("Admins", False), ("Consultants", False)]
        for rlc in rlcs:
            for group in groups:
                AddMethods.add_group(group, rlc.id)
        return list(Group.objects.all())


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
            us = UserProfile(
                email=user[0], name=user[1], is_superuser=user[2], is_active=True
            )
            us.set_password(user[3])
        elif user.__len__() == 5:
            us = UserProfile(
                id=user[0],
                email=user[1],
                name=user[2],
                is_superuser=user[3],
                is_active=True,
            )
            us.set_password(user[4])
        elif user.__len__() == 9:
            us = UserProfile(
                id=user[0],
                email=user[1],
                name=user[2],
                phone_number=user[4],
                street=user[5],
                city=user[6],
                postal_code=user[7],
                rlc_id=user[8],
            )
            us.birthday = AddMethods.generate_date(user[3])
            us.set_password("qwe123")
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
            lc = Rlc(
                id=rlc[0],
                name=rlc[1],
                uni_tied=rlc[2],
                part_of_umbrella=rlc[3],
                note=rlc[4],
            )
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
        try:
            perm.save()
        except:
            pass

    @staticmethod
    def add_folder_permission(permission):
        if isinstance(permission, str):
            perm = FolderPermission(name=permission)
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
        try:
            t.save()
        except:
            pass

    @staticmethod
    def add_record_document_tag(tag):
        if tag.__len__() == 1:
            t = RecordDocumentTag(name=tag[0])
        elif tag.__len__() == 2:
            t = RecordDocumentTag(id=tag[0], name=tag[1])
        else:
            raise AttributeError
        try:
            t.save()
        except:
            pass

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
        try:
            c.save()
        except:
            pass

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
            g = Group(
                id=group[0],
                creator_id=group[1],
                from_rlc_id=rlc_id,
                name=group[2],
                visible=group[3],
            )
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
            g = Group(
                id=group[0],
                creator_id=group[1],
                from_rlc_id=group[2],
                name=group[3],
                visible=group[4],
            )
            g.save()
            for user_id in group[5]:
                g.group_members.add(UserProfile.objects.get(pk=user_id))
        else:
            raise AttributeError
        g.save()

    @staticmethod
    def generate_date(information):
        return datetime(information[0], information[1], information[2]).replace(
            tzinfo=pytz.timezone(settings.TIME_ZONE)
        )

    @staticmethod
    def generate_datetime(information):
        return datetime(
            information[0],
            information[1],
            information[2],
            information[3],
            information[4],
            information[5],
            information[6],
        ).replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
