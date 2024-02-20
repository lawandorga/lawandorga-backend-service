- Email Model (Speichert uns die Emails ab) CHECK
- Email Collector (Holt uns die Emails aus dem IMAP Postfach) CHECK
  - Fragen: Wie oft soll er die Emails holen? Können Emails vergessen werden weil der user sie verschoben hat?
  - Verschlüsselt die Emails mit dem Ordner Public Key über Symmetric Key LATER
- Frontend Neuer Punkt in den Ordnern (Ausklappen) CHECK
- Endpunkt zum Abholden der Emails für Ordner X CHECK
- Usecase zum als gelesen markieren von Emails CHECK
- Funktion zum erstellen der Postfächer pro RLC CHECK
- Funktion zum Kopieren der CC-Email für einen Ordner CHECK



Reihenfolge:
1. Email Model (Johannes)
2. Erstellen der Postfächer (Daniel)
3. Email Collector (credentials für IMAP) | abhängigkeit zu email model (Johannes if Time)
4. Frontend Punkt erstellen und dark Release (Leandra)
