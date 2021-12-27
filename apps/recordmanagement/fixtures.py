from apps.recordmanagement.models import RecordTemplate, RecordStandardField, RecordEncryptedStandardField, \
    RecordUsersField, RecordStateField, RecordSelectField, RecordMultipleField
from django.db import transaction


def create_default_record_template(rlc):
    with transaction.atomic():
        template = RecordTemplate.objects.create(name='Default Record Template', rlc=rlc)
        RecordStandardField.objects.create(template=template, order=10, name='Token')
        RecordStandardField.objects.create(template=template, order=20, name='First contact date', field_type='DATE')
        RecordStandardField.objects.create(template=template, order=30, name='Last contact date',
                                           field_type='DATETIME-LOCAL')
        RecordStandardField.objects.create(template=template, order=40, name='First consultation',
                                           field_type='DATETIME-LOCAL')
        RecordStandardField.objects.create(template=template, order=50, name='Official Note')
        RecordUsersField.objects.create(template=template, order=60, name='Consultants')
        RecordMultipleField.objects.create(template=template, order=70, name='Tags', options=get_all_tags())
        options = ['Open', 'Closed', 'Waiting', 'Working']
        RecordStateField.objects.create(template=template, order=80, name='State', options=options)
        RecordEncryptedStandardField.objects.create(template=template, order=90, name='Note', field_type='TEXTAREA')
        RecordEncryptedStandardField.objects.create(template=template, order=100, name='Consultant Team')
        RecordEncryptedStandardField.objects.create(template=template, order=110, name='Lawyer')
        RecordEncryptedStandardField.objects.create(template=template, order=120, name='Related Persons')
        RecordEncryptedStandardField.objects.create(template=template, order=130, name='Contact')
        RecordEncryptedStandardField.objects.create(template=template, order=135, name='Foreign Token')
        RecordEncryptedStandardField.objects.create(template=template, order=140, name='BAMF Token')
        RecordEncryptedStandardField.objects.create(template=template, order=145, name='Circumstances')
        RecordEncryptedStandardField.objects.create(template=template, order=150, name='First Correspondence',
                                                    field_type='TEXTAREA')
        RecordEncryptedStandardField.objects.create(template=template, order=160, name='Next Steps',
                                                    field_type='TEXTAREA')
        RecordEncryptedStandardField.objects.create(template=template, order=170, name='Status described',
                                                    field_type='TEXTAREA')
        RecordEncryptedStandardField.objects.create(template=template, order=180, name='Additional facts',
                                                    field_type='TEXTAREA')
        RecordEncryptedStandardField.objects.create(template=template, order=190, name='Client name')
        RecordStandardField.objects.create(template=template, order=200, name='Birthday', field_type='DATE')
        RecordSelectField.objects.create(template=template, order=210, name='Origin Country',
                                         options=get_all_countries())
        RecordEncryptedStandardField.objects.create(template=template, order=220, name='Phone')
        RecordEncryptedStandardField.objects.create(template=template, order=230, name='Client Note',
                                                    field_type='TEXTAREA')


def get_all_tags():
    return ["Abschiebung", "Anhörung", "Arbeitserlaubnis", "Asylantrag", "Asylbewerberleistungsgesetz",
            "Aufenthaltserlaubnis", "Aufenthaltsgestattung", "Ausbildung", "Ausbildungsduldung", "Dublin IV", "Duldung",
            "Eheschließung", "Einbürgerung", "Eines Kindes im Asylverfahren", "Familienasyl", "Familiennachzug",
            "Familienzusammenführung nach Dublin III", "Flüchtlingseigenschaft", "Folgeantrag", "Geburt ",
            "Geschwisternachzug", "illegale Ausreise aus dem Bundesgebiet", "Kinder anerkennen", "Kirchenasyl",
            "Krankheit im Asylverfahren", "Mitwirkungspflichten", "Negativbescheid", "Nichtbetreiben des Verfahrens",
            "Niederlassungserlaubnis", "Passbeschaffung", "Relocation", "Resettlement", "Rücknahme der Asyberechtigung",
            "Sonstiges", "Staatsbürgerschaft", "Strafverfolgung", "Studium", "subsidiärer Schutz", "Test", "Übungsfall",
            "UmF", "Untätigkeitsklage", "Unterbringung im Asylverfahren", "Untertauchen", "Verlobung", "Visum",
            "Wechsel der Unterkunft", "Widerruf der Asylberechtigung", "Wohnsitzauflage", "Zweitantrag"]


def get_all_countries():
    return ["Abchasien", "Afghanistan", "Ägypten", "Albanien", "Algerien", "Andorra", "Angola", "Antigua und Barbuda",
            "Äquatorialguinea", "Argentinien", "Armenien", "Arzach", "Aserbaidschan", "Äthiopien", "Australien",
            "Bahamas", "Bahrain", "Bangladesch", "Barbados", "Belgien", "Belize", "Benin", "Bhutan", "Bolivien",
            "Bosnien und Herzegowina", "Botswana", "Brasilien", "Brunei", "Bulgarien", "Burkina Faso", "Burundi",
            "Chile", "Republik China", "Volksrepublik China", "Cookinseln", "Costa Rica", "Dänemark", "Deutschland",
            "Dominica", "Dominikanische Republik", "Dschibuti", "Ecuador", "El Salvador", "Elfenbeinküste", "Eritrea",
            "Estland", "Fidschi", "Finnland", "Frankreich", "Gabun", "Gambia", "Georgien", "Ghana", "Grenada",
            "Griechenland", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Indien",
            "Indonesien", "Irak", "Iran", "Irland", "Island", "Israel", "Italien", "Jamaika", "Japan", "Jemen",
            "Jordanien", "Kambodscha", "Kamerun", "Kanada", "Kap Verde", "Kasachstan", "Katar", "Kenia", "Kirgisistan",
            "Kiribati", "Kolumbien", "Komoren", "Kongo, Demokratische Republik", "Kongo, Republik", "Nordkorea",
            "Südkorea", "Kosovo", "Kroatien", "Kuba", "Kuwait", "Laos", "Lesotho", "Lettland", "Libanon", "Liberia",
            "Libyen", "Liechtenstein", "Litauen", "Luxemburg", "Madagaskar", "Malawi", "Malaysia", "Malediven", "Mali",
            "Malta", "Marokko", "Marshallinseln", "Mauretanien", "Mauritius", "Mexiko", "Mikronesien", "Moldau",
            "Monaco", "Mongolei", "Montenegro", "Mosambik", "Myanmar", "Namibia", "Nauru", "Nepal", "Neuseeland",
            "Nicaragua", "Niederlande", "Curaçao", "Sint Maarten", "Niger", "Nigeria", "Niue", "Nordmazedonien",
            "Nordzypern", "Norwegen", "Oman", "Österreich", "Osttimor / Timor-Leste", "Pakistan", "Palästina", "Palau",
            "Panama", "Papua-Neuguinea", "Paraguay", "Peru", "Philippinen", "Polen", "Portugal", "Ruanda", "Rumänien",
            "Russland", "Salomonen", "Sambia", "Samoa", "San Marino", "São Tomé und Príncipe", "Saudi-Arabien",
            "Schweden", "Schweiz", "Senegal", "Serbien", "Seychellen", "Sierra Leone", "Simbabwe", "Singapur",
            "Slowakei", "Slowenien", "Somalia", "Somaliland", "Spanien", "Sri Lanka", "St. Kitts und Nevis",
            "St. Lucia", "St. Vincent und die Grenadinen", "Südafrika", "Sudan ", "Südossetien", "Südsudan", "Suriname",
            "Swasiland", "Syrien", "Tadschikistan", "Tansania", "Thailand", "Togo", "Tonga", "Transnistrien",
            "Trinidad und Tobago", "Tschad", "Tschechien", "Tunesien", "Türkei", "Turkmenistan", "Tuvalu", "Uganda",
            "Ukraine", "Ungarn", "Uruguay", "Usbekistan", "Vanuatu", "Vatikanstadt", "Venezuela",
            "Vereinigte Arabische Emirate", "Vereinigte Staaten", "Vereinigtes Königreich", "Vietnam", "Weißrussland",
            "Westsahara", "Zentralafrikanische Republik", "Zypern", "Unbekanntes Herkunftsland"]
