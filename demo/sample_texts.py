"""Sample German texts for PII detection demo."""

SAMPLES = {
    "Customer Support Email": """Sehr geehrter Herr Dr. Hans Müller,

vielen Dank für Ihre Anfrage bezüglich Ihres SAP-Kontos. Wir haben Ihre Nachricht erhalten und möchten Ihnen bei der Lösung Ihres Anliegens helfen.

Zur Verifizierung Ihrer Identität haben wir folgende Daten in unserem System:

Persönliche Daten:
- Vollständiger Name: Dr. Hans Müller
- Geburtsdatum: 15.03.1985
- Anschrift: Musterstraße 42, 80331 München

Kontaktdaten:
- E-Mail: hans.mueller@example.de
- Mobiltelefon: +49 171 1234567
- Festnetz: 089 987654321

Zahlungsinformationen:
- IBAN: DE89370400440532013000
- Kreditkarte: 4532015112830366

Identifikationsdokumente:
- Personalausweis-Nr.: L01X00T471

Bitte bestätigen Sie diese Informationen, damit wir Ihr Anliegen schnellstmöglich bearbeiten können. Falls Sie Änderungen an Ihren Daten vornehmen möchten, kontaktieren Sie uns bitte unter der oben genannten Telefonnummer.

Mit freundlichen Grüßen,
Maria Schmidt
SAP Data Protection Team
E-Mail: m.schmidt@sap.com
Telefon: +49 6227 7-47474""",
    "HR Employee Record": """PERSONALAKTE - VERTRAULICH

Mitarbeiter-ID: SAP-2024-0815
Erstellungsdatum: 01.01.2024
Abteilung: EDT Data Protection

═══════════════════════════════════════════════════════

PERSÖNLICHE INFORMATIONEN

Name: Elisabeth Schneider
Titel: Senior Data Protection Specialist
Geburtsdatum: 22.07.1988
Geburtsort: Berlin

Aktuelle Adresse:
Berliner Straße 123
10115 Berlin
Deutschland

Kontaktinformationen:
- Dienstliche E-Mail: e.schneider@sap.com
- Private E-Mail: elisabeth.schneider@gmail.com
- Mobiltelefon: +49 176 98765432
- Festnetz privat: 030 12345678
- Notfallkontakt: Thomas Schneider, +49 171 5551234

═══════════════════════════════════════════════════════

IDENTIFIKATION & FINANZEN

Personalausweis-Nr.: T22000129
Steuer-ID: 12 345 678 901

Bankverbindung für Gehaltsüberweisung:
- Kontoinhaber: Elisabeth Schneider
- IBAN: DE91100000000123456789
- BIC: MARKDEF1100

Firmenkreditkarte:
- Kartennummer: 5425233430109903
- Gültig bis: 12/2026

═══════════════════════════════════════════════════════

IT-ZUGANGSDATEN

Benutzername: eschneider
Letzte IP-Adresse: 192.168.1.100
VPN-Zugang: Aktiv
Letzter Login: 03.01.2024, 09:15 Uhr

═══════════════════════════════════════════════════════

Diese Akte enthält sensible personenbezogene Daten gemäß DSGVO Art. 9.
Zugriff nur für autorisierte HR-Mitarbeiter.""",
    "IT Support Ticket": """══════════════════════════════════════════════════════════════
SAP INTERNAL IT SUPPORT - TICKET #INC-2024-78542
══════════════════════════════════════════════════════════════

Status: In Bearbeitung
Priorität: Hoch
Kategorie: Netzwerk / VPN
Erstellt: 03.01.2024, 14:23 Uhr

──────────────────────────────────────────────────────────────
BENUTZERINFORMATIONEN
──────────────────────────────────────────────────────────────

Melder: Dr. Thomas Weber
Position: Solution Architect
Abteilung: Cloud Infrastructure
Standort: Walldorf, Gebäude 3

Kontaktdaten:
- E-Mail: t.weber@sap.com
- Telefon: +49 6227 7-12345
- Mobil: +49 172 9876543

Technische Details:
- Benutzername: tweber
- Arbeitsplatz-ID: WDF-PC-4711
- IP-Adresse (intern): 10.128.45.67
- IP-Adresse (VPN): 192.168.1.100
- MAC-Adresse: 00:1A:2B:3C:4D:5E

──────────────────────────────────────────────────────────────
PROBLEMBESCHREIBUNG
──────────────────────────────────────────────────────────────

Der Benutzer meldet wiederholte VPN-Verbindungsabbrüche seit dem
letzten Windows-Update. Die Verbindung trennt sich alle 15-20
Minuten automatisch.

Betroffene Systeme:
- SAP S/4HANA (Zugriff über VPN)
- SAP BTP Cloud Foundry
- Interne Wiki-Systeme

Der Benutzer hat bereits folgende Schritte durchgeführt:
1. VPN-Client neu installiert
2. Netzwerkadapter zurückgesetzt
3. Windows Firewall-Einstellungen überprüft

──────────────────────────────────────────────────────────────
BEARBEITUNGSHISTORIE
──────────────────────────────────────────────────────────────

[03.01.2024 14:30] Ticket zugewiesen an: Anna Müller (a.mueller@sap.com)
[03.01.2024 14:45] Remote-Diagnose gestartet
[03.01.2024 15:00] Rückruf vereinbart unter: +49 172 9876543

──────────────────────────────────────────────────────────────
INTERNE NOTIZEN (VERTRAULICH)
──────────────────────────────────────────────────────────────

Benutzer-ID im Active Directory: S-1-5-21-3623811015-3361044348-30300820-1013
Letzte bekannte externe IP: 87.123.45.67
Router-Konfiguration überprüfen für Standort Berlin.

══════════════════════════════════════════════════════════════""",
}

DEFAULT_SAMPLE = "Customer Support Email"
