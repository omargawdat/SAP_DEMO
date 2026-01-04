"""Sample German texts for PII detection demo."""

SAMPLES = {
    "Customer Support Email": """Sehr geehrter Herr Hans Müller,

vielen Dank für Ihre Anfrage. Ihre Kundendaten:
- Email: hans.mueller@example.de
- Telefon: +49 171 1234567
- IBAN: DE89370400440532013000
- Personalausweis: L01X00T471

Mit freundlichen Grüßen,
SAP Data Protection Team""",
    "Job Application": """Bewerbung von Maria Schmidt
Adresse: Hauptstraße 42, 10115 Berlin
Geburtsdatum: 15.03.1990
Kontakt: maria.schmidt@gmail.com, 0171-9876543
Kreditkarte: 4532015112830366""",
    "IT Support Ticket": """Ticket #12345
Benutzer: Dr. Thomas Weber
IP-Adresse: 192.168.1.100
Email: t.weber@company.de
Problem: VPN-Verbindung fehlgeschlagen
Telefon für Rückruf: 030 12345678""",
    "Mixed PII Document": """Kundenprofil erstellt am 15.01.2024

Name: Elisabeth Schneider
Anschrift: Berliner Straße 123, 80331 München
Kontaktdaten:
  - Email: e.schneider@web.de
  - Mobil: +49 176 98765432
  - Festnetz: 089 123456

Zahlungsinformationen:
  - IBAN: DE89370400440532013000
  - Kreditkarte: 5425233430109903

Identifikation:
  - Personalausweis: T22000129
  - IP der Registrierung: 10.0.0.55""",
}

DEFAULT_SAMPLE = "Customer Support Email"
