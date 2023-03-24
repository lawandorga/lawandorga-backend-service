from django.db import transaction

from core.data_sheets.models import (
    RecordEncryptedStandardField,
    RecordMultipleField,
    RecordSelectField,
    RecordStandardField,
    RecordStateField,
    RecordTemplate,
    RecordUsersField,
)


def create_default_record_template(rlc):
    with transaction.atomic():
        template = RecordTemplate.objects.create(
            name="Default Record Template", rlc=rlc
        )
        RecordStandardField.objects.create(template=template, order=10, name="Token")
        RecordStandardField.objects.create(
            template=template, order=20, name="First contact date", field_type="DATE"
        )
        RecordStandardField.objects.create(
            template=template,
            order=30,
            name="Last contact date",
            field_type="DATETIME-LOCAL",
        )
        RecordStandardField.objects.create(
            template=template,
            order=40,
            name="First consultation",
            field_type="DATETIME-LOCAL",
        )
        RecordStandardField.objects.create(
            template=template, order=50, name="Official Note"
        )
        RecordUsersField.objects.create(template=template, order=60, name="Consultants")
        RecordMultipleField.objects.create(
            template=template, order=70, name="Tags", options=get_all_tags()
        )
        options = ["Open", "Closed", "Waiting", "Working"]
        RecordStateField.objects.create(
            template=template, order=80, name="State", options=options
        )
        RecordEncryptedStandardField.objects.create(
            template=template, order=90, name="Note", field_type="TEXTAREA"
        )
        RecordEncryptedStandardField.objects.create(
            template=template, order=100, name="Consultant Team"
        )
        RecordEncryptedStandardField.objects.create(
            template=template, order=110, name="Lawyer"
        )
        RecordEncryptedStandardField.objects.create(
            template=template, order=120, name="Related Persons"
        )
        RecordEncryptedStandardField.objects.create(
            template=template, order=130, name="Contact"
        )
        RecordEncryptedStandardField.objects.create(
            template=template, order=135, name="Foreign Token"
        )
        RecordEncryptedStandardField.objects.create(
            template=template, order=140, name="BAMF Token"
        )
        RecordEncryptedStandardField.objects.create(
            template=template, order=145, name="Circumstances"
        )
        RecordEncryptedStandardField.objects.create(
            template=template,
            order=150,
            name="First Correspondence",
            field_type="TEXTAREA",
        )
        RecordEncryptedStandardField.objects.create(
            template=template, order=160, name="Next Steps", field_type="TEXTAREA"
        )
        RecordEncryptedStandardField.objects.create(
            template=template, order=170, name="Status described", field_type="TEXTAREA"
        )
        RecordEncryptedStandardField.objects.create(
            template=template, order=180, name="Additional facts", field_type="TEXTAREA"
        )
        RecordEncryptedStandardField.objects.create(
            template=template, order=190, name="Client name"
        )
        RecordStandardField.objects.create(
            template=template, order=200, name="Birthday", field_type="DATE"
        )
        RecordSelectField.objects.create(
            template=template,
            order=210,
            name="Origin Country",
            options=get_all_countries(),
        )
        RecordEncryptedStandardField.objects.create(
            template=template, order=220, name="Phone"
        )
        RecordEncryptedStandardField.objects.create(
            template=template, order=230, name="Client Note", field_type="TEXTAREA"
        )


def get_all_tags():
    return [
        "Abschiebung",
        "Anhörung",
        "Arbeitserlaubnis",
        "Asylantrag",
        "Asylbewerberleistungsgesetz",
        "Aufenthaltserlaubnis",
        "Aufenthaltsgestattung",
        "Ausbildung",
        "Ausbildungsduldung",
        "Dublin IV",
        "Duldung",
        "Eheschließung",
        "Einbürgerung",
        "Eines Kindes im Asylverfahren",
        "Familienasyl",
        "Familiennachzug",
        "Familienzusammenführung nach Dublin III",
        "Flüchtlingseigenschaft",
        "Folgeantrag",
        "Geburt ",
        "Geschwisternachzug",
        "illegale Ausreise aus dem Bundesgebiet",
        "Kinder anerkennen",
        "Kirchenasyl",
        "Krankheit im Asylverfahren",
        "Mitwirkungspflichten",
        "Negativbescheid",
        "Nichtbetreiben des Verfahrens",
        "Niederlassungserlaubnis",
        "Passbeschaffung",
        "Relocation",
        "Resettlement",
        "Rücknahme der Asyberechtigung",
        "Sonstiges",
        "Staatsbürgerschaft",
        "Strafverfolgung",
        "Studium",
        "subsidiärer Schutz",
        "Test",
        "Übungsfall",
        "UmF",
        "Untätigkeitsklage",
        "Unterbringung im Asylverfahren",
        "Untertauchen",
        "Verlobung",
        "Visum",
        "Wechsel der Unterkunft",
        "Widerruf der Asylberechtigung",
        "Wohnsitzauflage",
        "Zweitantrag",
    ]


def get_all_countries():
    return [
        "Afghanistan",
        "Albania",
        "Algeria",
        "American Samoa",
        "AndorrA",
        "Angola",
        "Anguilla",
        "Antarctica",
        "Antigua and Barbuda",
        "Argentina",
        "Armenia",
        "Aruba",
        "Australia",
        "Austria",
        "Azerbaijan",
        "Bahamas",
        "Bahrain",
        "Bangladesh",
        "Barbados",
        "Belarus",
        "Belgium",
        "Belize",
        "Benin",
        "Bermuda",
        "Bhutan",
        "Bolivia",
        "Bosnia and Herzegovina",
        "Botswana",
        "Bouvet Island",
        "Brazil",
        "British Indian Ocean Territory",
        "Brunei Darussalam",
        "Bulgaria",
        "Burkina Faso",
        "Burundi",
        "Cambodia",
        "Cameroon",
        "Canada",
        "Cape Verde",
        "Cayman Islands",
        "Central African Republic",
        "Chad",
        "Chile",
        "China",
        "Christmas Island",
        "Cocos (Keeling) Islands",
        "Colombia",
        "Comoros",
        "Congo",
        "Congo, The Democratic Republic of the",
        "Cook Islands",
        "Costa Rica",
        'Cote D"Ivoire',
        "Croatia",
        "Cuba",
        "Cyprus",
        "Czech Republic",
        "Denmark",
        "Djibouti",
        "Dominica",
        "Dominican Republic",
        "Ecuador",
        "Egypt",
        "El Salvador",
        "Equatorial Guinea",
        "Eritrea",
        "Estonia",
        "Ethiopia",
        "Falkland Islands (Malvinas)",
        "Faroe Islands",
        "Fiji",
        "Finland",
        "France",
        "French Guiana",
        "French Polynesia",
        "French Southern Territories",
        "Gabon",
        "Gambia",
        "Georgia",
        "Germany",
        "Ghana",
        "Gibraltar",
        "Greece",
        "Greenland",
        "Grenada",
        "Guadeloupe",
        "Guam",
        "Guatemala",
        "Guernsey",
        "Guinea",
        "Guinea-Bissau",
        "Guyana",
        "Haiti",
        "Heard Island and Mcdonald Islands",
        "Holy See (Vatican City State)",
        "Honduras",
        "Hong Kong",
        "Hungary",
        "Iceland",
        "India",
        "Indonesia",
        "Iran, Islamic Republic Of",
        "Iraq",
        "Ireland",
        "Isle of Man",
        "Israel",
        "Italy",
        "Jamaica",
        "Japan",
        "Jersey",
        "Jordan",
        "Kazakhstan",
        "Kenya",
        "Kiribati",
        "Kosovo",
        "Kuwait",
        "Kyrgyzstan",
        'Lao People"S Democratic Republic',
        "Latvia",
        "Lebanon",
        "Lesotho",
        "Liberia",
        "Libyan Arab Jamahiriya",
        "Liechtenstein",
        "Lithuania",
        "Luxembourg",
        "Macao",
        "Macedonia, The Former Yugoslav Republic of",
        "Madagascar",
        "Malawi",
        "Malaysia",
        "Maldives",
        "Mali",
        "Malta",
        "Marshall Islands",
        "Martinique",
        "Mauritania",
        "Mauritius",
        "Mayotte",
        "Mexico",
        "Micronesia, Federated States of",
        "Moldova, Republic of",
        "Monaco",
        "Mongolia",
        "Montenegro",
        "Montserrat",
        "Morocco",
        "Mozambique",
        "Myanmar",
        "Namibia",
        "Nauru",
        "Nepal",
        "Netherlands",
        "Netherlands Antilles",
        "New Caledonia",
        "New Zealand",
        "Nicaragua",
        "Niger",
        "Nigeria",
        "Niue",
        "Norfolk Island",
        "North Korea",
        "Northern Mariana Islands",
        "Norway",
        "Oman",
        "Pakistan",
        "Palau",
        "Palestinian Territory, Occupied",
        "Panama",
        "Papua New Guinea",
        "Paraguay",
        "Peru",
        "Philippines",
        "Pitcairn",
        "Poland",
        "Portugal",
        "Puerto Rico",
        "Qatar",
        "Reunion",
        "Romania",
        "Russian Federation",
        "RWANDA",
        "Saint Helena",
        "Saint Kitts and Nevis",
        "Saint Lucia",
        "Saint Pierre and Miquelon",
        "Saint Vincent and the Grenadines",
        "Samoa",
        "San Marino",
        "Sao Tome and Principe",
        "Saudi Arabia",
        "Senegal",
        "Serbia",
        "Seychelles",
        "Sierra Leone",
        "Singapore",
        "Slovakia",
        "Slovenia",
        "Solomon Islands",
        "Somalia",
        "South Africa",
        "South Georgia and the South Sandwich Islands",
        "South Korea",
        "South Sudan",
        "Spain",
        "Sri Lanka",
        "Sudan",
        "Suriname",
        "Svalbard and Jan Mayen",
        "Swaziland",
        "Sweden",
        "Switzerland",
        "Syrian Arab Republic",
        "Taiwan, Province of China",
        "Tajikistan",
        "Tanzania, United Republic of",
        "Thailand",
        "Timor-Leste",
        "Togo",
        "Tokelau",
        "Tonga",
        "Trinidad and Tobago",
        "Tunisia",
        "Turkey",
        "Turkmenistan",
        "Turks and Caicos Islands",
        "Tuvalu",
        "Uganda",
        "Ukraine",
        "United Arab Emirates",
        "United Kingdom",
        "United States",
        "United States Minor Outlying Islands",
        "Uruguay",
        "Uzbekistan",
        "Vanuatu",
        "Venezuela",
        "Viet Nam",
        "Virgin Islands, British",
        "Virgin Islands, U.S.",
        "Wallis and Futuna",
        "Western Sahara",
        "Yemen",
        "Zambia",
        "Zimbabwe",
        "Stateless",
        "Unknown",
    ]
