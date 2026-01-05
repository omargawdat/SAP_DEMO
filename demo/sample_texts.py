"""Sample German texts for PII detection demo with expected annotations."""

SAMPLES = {
    "Tricky Cases (LLM Demo)": {
        "text": """Betreff: Kontodaten für Max Mustermann

Personalausweis-Nr.: L01X00T471
Reisepass-Nr.: C01X00T478
Steuer-ID: 12345678901

Kontakt: max.mustermann@sap.com
Telefon: +49 171 1234567

Firma: SAP Deutschland
Produkt: SAP S/4HANA
Straße: Dietmar-Hopp-Allee 16, Walldorf

Bearbeitet von: Anna Schmidt""",
        "annotations": [
            {"type": "NAME", "text": "Max Mustermann"},
            {"type": "NAME", "text": "Anna Schmidt"},
            {"type": "GERMAN_ID", "text": "L01X00T471"},
            {"type": "EMAIL", "text": "max.mustermann@sap.com"},
            {"type": "PHONE", "text": "+49 171 1234567"},
            {"type": "ADDRESS", "text": "Dietmar-Hopp-Allee 16"},
            {"type": "ADDRESS", "text": "Walldorf"},
        ],
    },
    "Customer Support Email": {
        "text": """Sehr geehrter Herr Dr. Hans Müller,

vielen Dank für Ihre Anfrage bezüglich Ihres SAP-Kontos. Wir haben Ihre Nachricht erhalten und möchten Ihnen bei der Lösung Ihres Anliegens helfen.

Zur Verifizierung Ihrer Identität haben wir folgende Daten in unserem System:

Persönliche Daten:
- Vollständiger Name: Dr. Hans Müller
- Geburtsdatum: 15.03.1985
- Anschrift: Musterstraße 42, 80331 München
- Zweitwohnsitz: Berliner Allee 15, 10115 Berlin

Kontaktdaten:
- E-Mail (privat): hans.mueller@example.de
- E-Mail (geschäftlich): h.mueller@sap.com
- Mobiltelefon: +49 171 1234567
- Festnetz: 089 987654321
- Fax: +49 89 12345678

Zahlungsinformationen:
- IBAN (Hauptkonto): DE89370400440532013000
- IBAN (Sparkonto): DE44500105175407324931
- Kreditkarte (Visa): 4532015112830366
- Kreditkarte (Mastercard): 5425233430109903

Identifikationsdokumente:
- Personalausweis-Nr.: L01X00T471
- Reisepass-Nr.: C01X00T478

Technische Daten:
- Letzte Login-IP: 192.168.1.100
- VPN-IP: 10.0.0.45

Bitte bestätigen Sie diese Informationen, damit wir Ihr Anliegen schnellstmöglich bearbeiten können. Falls Sie Änderungen an Ihren Daten vornehmen möchten, kontaktieren Sie uns bitte unter der oben genannten Telefonnummer.

Mit freundlichen Grüßen,
Maria Schmidt
SAP Data Protection Team
E-Mail: m.schmidt@sap.com
Telefon: +49 6227 7-47474

Kopie an: Peter Weber (p.weber@sap.com)""",
        "annotations": [
            # Names
            {"type": "NAME", "text": "Hans Müller"},
            {"type": "NAME", "text": "Maria Schmidt"},
            {"type": "NAME", "text": "Peter Weber"},
            # Date of birth
            {"type": "DATE_OF_BIRTH", "text": "15.03.1985"},
            # Addresses
            {"type": "ADDRESS", "text": "Musterstraße 42"},
            {"type": "ADDRESS", "text": "München"},
            {"type": "ADDRESS", "text": "Berliner Allee 15"},
            {"type": "ADDRESS", "text": "Berlin"},
            # Emails
            {"type": "EMAIL", "text": "hans.mueller@example.de"},
            {"type": "EMAIL", "text": "h.mueller@sap.com"},
            {"type": "EMAIL", "text": "m.schmidt@sap.com"},
            {"type": "EMAIL", "text": "p.weber@sap.com"},
            # Phones
            {"type": "PHONE", "text": "+49 171 1234567"},
            {"type": "PHONE", "text": "089 987654321"},
            {"type": "PHONE", "text": "+49 89 12345678"},
            {"type": "PHONE", "text": "+49 6227 7-47474"},
            # IBANs
            {"type": "IBAN", "text": "DE89370400440532013000"},
            {"type": "IBAN", "text": "DE44500105175407324931"},
            # Credit Cards
            {"type": "CREDIT_CARD", "text": "4532015112830366"},
            {"type": "CREDIT_CARD", "text": "5425233430109903"},
            # German IDs
            {"type": "GERMAN_ID", "text": "L01X00T471"},
            # IP Addresses
            {"type": "IP_ADDRESS", "text": "192.168.1.100"},
            {"type": "IP_ADDRESS", "text": "10.0.0.45"},
        ],
    },
    "HR Employee Record": {
        "text": """PERSONALAKTE - STRENG VERTRAULICH

Dokumenten-ID: HR-2024-00815
Erstellungsdatum: 01.01.2024
Letzte Aktualisierung: 15.06.2024
Abteilung: EDT Data Protection
Standort: Walldorf, Deutschland

═══════════════════════════════════════════════════════════════════════════════

PERSÖNLICHE INFORMATIONEN

Vollständiger Name: Elisabeth Maria Schneider
Geburtsname: Elisabeth Maria Weber
Geburtsdatum: 22.07.1988
Geburtsort: Frankfurt am Main
Staatsangehörigkeit: Deutsch
Familienstand: Verheiratet

Aktuelle Adresse:
Berliner Straße 123
10115 Berlin
Deutschland

Frühere Adresse:
Hauptstraße 45
60311 Frankfurt am Main

═══════════════════════════════════════════════════════════════════════════════

KONTAKTINFORMATIONEN

- Dienstliche E-Mail: e.schneider@sap.com
- Private E-Mail: elisabeth.schneider@gmail.com
- Zweit-E-Mail: e.weber1988@web.de
- Mobiltelefon (dienstlich): +49 176 98765432
- Mobiltelefon (privat): +49 151 12345678
- Festnetz privat: 030 12345678
- Festnetz Eltern: 069 87654321

Notfallkontakte:
1. Thomas Schneider (Ehemann): +49 171 5551234, t.schneider@gmail.com
2. Maria Weber (Mutter): +49 69 11223344, m.weber@gmx.de

═══════════════════════════════════════════════════════════════════════════════

IDENTIFIKATION & BEHÖRDLICHE DATEN

Personalausweis-Nr.: T22000129
Reisepass-Nr.: C3X4Y5Z67
Führerschein-Nr.: B072RFM009
Steuer-ID: 12 345 678 901
Sozialversicherungsnummer: 65 170788 S 541

═══════════════════════════════════════════════════════════════════════════════

BANKVERBINDUNGEN & FINANZEN

Gehaltskonto:
- Kontoinhaber: Elisabeth Schneider
- Bank: Deutsche Bank
- IBAN: DE91100000000123456789
- BIC: DEUTDEDB

Sparkonto:
- IBAN: DE89370400440532013000

Firmenkreditkarte:
- Kartentyp: Mastercard Business
- Kartennummer: 5425233430109903
- Gültig bis: 12/2026
- CVV: Im Safe hinterlegt

Private Kreditkarte:
- Kartentyp: Visa
- Kartennummer: 4111111111111111
- Gültig bis: 08/2025

═══════════════════════════════════════════════════════════════════════════════

IT-ZUGANGSDATEN & SYSTEME

Benutzername: eschneider
E-Mail-Alias: elisabeth.schneider@sap.com
Active Directory: SAP\\eschneider

Netzwerkdaten:
- Arbeitsplatz-IP: 192.168.1.100
- VPN-IP (extern): 87.123.45.67
- Home-Office Router: 192.168.178.1
- IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334

Letzte Logins:
- 15.06.2024, 09:15 Uhr (IP: 192.168.1.100)
- 14.06.2024, 08:30 Uhr (IP: 87.123.45.67)

═══════════════════════════════════════════════════════════════════════════════

WEITERE MITARBEITER IM TEAM

- Projektleiter: Dr. Michael Braun (m.braun@sap.com, +49 6227 7-12345)
- Teamkollege: Anna Hoffmann (a.hoffmann@sap.com, +49 6227 7-67890)
- Assistenz: Julia Klein (j.klein@sap.com, +49 6227 7-11111)

═══════════════════════════════════════════════════════════════════════════════

Diese Akte enthält sensible personenbezogene Daten gemäß DSGVO Art. 9.
Zugriff nur für autorisierte HR-Mitarbeiter.
Letzte Prüfung durch: Datenschutzbeauftragter Thomas Müller (t.mueller@sap.com)""",
        "annotations": [
            # Names (all persons mentioned)
            {"type": "NAME", "text": "Elisabeth Maria Schneider"},
            {"type": "NAME", "text": "Elisabeth Maria Weber"},
            {"type": "NAME", "text": "Elisabeth Schneider"},
            {"type": "NAME", "text": "Thomas Schneider"},
            {"type": "NAME", "text": "Maria Weber"},
            {"type": "NAME", "text": "Michael Braun"},
            {"type": "NAME", "text": "Anna Hoffmann"},
            {"type": "NAME", "text": "Julia Klein"},
            {"type": "NAME", "text": "Thomas Müller"},
            # Dates of birth
            {"type": "DATE_OF_BIRTH", "text": "22.07.1988"},
            # Addresses (matching detector spans - includes postal codes when detected together)
            {"type": "ADDRESS", "text": "Berliner Straße 123"},
            {"type": "ADDRESS", "text": "10115 Berlin Deutschland"},
            {"type": "ADDRESS", "text": "60311 Frankfurt am Main"},
            # Emails
            {"type": "EMAIL", "text": "e.schneider@sap.com"},
            {"type": "EMAIL", "text": "elisabeth.schneider@gmail.com"},
            {"type": "EMAIL", "text": "e.weber1988@web.de"},
            {"type": "EMAIL", "text": "elisabeth.schneider@sap.com"},
            {"type": "EMAIL", "text": "t.schneider@gmail.com"},
            {"type": "EMAIL", "text": "m.weber@gmx.de"},
            {"type": "EMAIL", "text": "m.braun@sap.com"},
            {"type": "EMAIL", "text": "a.hoffmann@sap.com"},
            {"type": "EMAIL", "text": "j.klein@sap.com"},
            {"type": "EMAIL", "text": "t.mueller@sap.com"},
            # Phones
            {"type": "PHONE", "text": "+49 176 98765432"},
            {"type": "PHONE", "text": "+49 151 12345678"},
            {"type": "PHONE", "text": "030 12345678"},
            {"type": "PHONE", "text": "069 87654321"},
            {"type": "PHONE", "text": "+49 171 5551234"},
            {"type": "PHONE", "text": "+49 69 11223344"},
            {"type": "PHONE", "text": "+49 6227 7-12345"},
            {"type": "PHONE", "text": "+49 6227 7-67890"},
            {"type": "PHONE", "text": "+49 6227 7-11111"},
            # German IDs
            {"type": "GERMAN_ID", "text": "T22000129"},
            # IBANs
            {"type": "IBAN", "text": "DE91100000000123456789"},
            {"type": "IBAN", "text": "DE89370400440532013000"},
            # Credit Cards
            {"type": "CREDIT_CARD", "text": "5425233430109903"},
            {"type": "CREDIT_CARD", "text": "4111111111111111"},
            # IP Addresses (some appear twice: in Netzwerkdaten and Letzte Logins)
            {"type": "IP_ADDRESS", "text": "192.168.1.100"},
            {"type": "IP_ADDRESS", "text": "192.168.1.100"},
            {"type": "IP_ADDRESS", "text": "87.123.45.67"},
            {"type": "IP_ADDRESS", "text": "87.123.45.67"},
            {"type": "IP_ADDRESS", "text": "192.168.178.1"},
            {"type": "IP_ADDRESS", "text": "2001:0db8:85a3:0000:0000:8a2e:0370:7334"},
        ],
    },
}

DEFAULT_SAMPLE = "Customer Support Email"
