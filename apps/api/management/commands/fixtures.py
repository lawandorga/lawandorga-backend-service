from apps.api.models import *
from apps.collab.models import CollabPermission
from apps.collab.static.collab_permissions import get_all_collab_permission_strings
from apps.recordmanagement.models import OriginCountry
from apps.static.permissions import get_all_permissions_strings
from apps.files.models import FolderPermission
from apps.files.static.folder_permissions import get_all_folder_permissions_strings


class Fixtures:
    # TODO: check create_real
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
    def create_real_permissions_no_duplicates():
        permissions = get_all_permissions_strings()
        for permission in permissions:
            if Permission.objects.filter(name=permission).count() == 0:
                AddMethods.add_permission(permission)

    @staticmethod
    def create_real_folder_permissions_no_duplicate():
        folder_permissions = get_all_folder_permissions_strings()
        for folder_permission in folder_permissions:
            if not FolderPermission.objects.filter(name=folder_permission).exists():
                AddMethods.add_folder_permission(folder_permission)

    @staticmethod
    def create_real_collab_permissions():
        collab_permissions = get_all_collab_permission_strings()
        for permission in collab_permissions:
            CollabPermission.objects.get_or_create(name=permission)


class AddMethods:
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
        else:
            raise AttributeError
        try:
            perm.save()
        except:
            pass

    @staticmethod
    def add_folder_permission(permission):
        if isinstance(permission, str):
            permission = FolderPermission(name=permission)
        permission.save()

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
