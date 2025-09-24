# Füllmanager - Erweiterte Füllvorgangsverwaltung

## Übersicht

Der Füllmanager ist eine erweiterte Komponente des WartungsManagers, die den kompletten Füllprozess von der Flaschenannahme bis zur Unterschrift dokumentiert und verwaltet.

## Features

### 1. Flaschenannahme
- Kundenauswahl mit automatischer Flaschenauflistung
- Visuelle Prüfung und TÜV-Kontrolle
- Ventilzustandserfassung
- Anmerkungen bei Auffälligkeiten

### 2. Füllparametereingabe
- Restdruck- und Zieldruckerfassung
- Gasgemisch-Konfiguration (O₂, He, N₂)
- Automatische Validierung (Summe = 100%)
- Live-Berechnung der Gaszusammensetzung

### 3. Füllvorgang
- Status-Tracking (angenommen → in_fuellung → abgeschlossen)
- Zeiterfassung für jeden Schritt
- Tatsächlicher Enddruck erfassbar
- Notizen während der Füllung

### 4. Berechnungen
- Automatische Preisberechnung basierend auf:
  - Helium: 0,095 €/Bar·Liter
  - Sauerstoff: 0,01 €/Bar·Liter
  - Luft/Stickstoff: 0,002 €/Bar·Liter
- MOD-Berechnungen (Maximum Operating Depth) für 1.2, 1.4 und 1.6 bar ppO₂
- END-Berechnung (Equivalent Air Depth) bei 30m

### 5. Digitale Unterschriften
- Touch-optimierte Unterschrifterfassung
- Separate Unterschriften für Kunde und Mitarbeiter
- Base64-kodierte Speicherung in der Datenbank
- Geräte- und IP-Adresserfassung
- Zeitstempel für jede Unterschrift

### 6. Belegdruck
- Automatische Druckansicht nach Abschluss
- Alle relevanten Daten auf einer A4-Seite
- Gasgemisch-Visualisierung
- Preisaufschlüsselung
- Digitale Unterschriften werden gedruckt

## Installation

1. **Migration ausführen:**
   ```batch
   FUELLMANAGER_MIGRATION.bat
   ```

2. **Server starten:**
   ```batch
   START_WARTUNGSMANAGER.bat
   ```

3. **Füllmanager aufrufen:**
   - Browser öffnen: http://localhost:5000
   - Navigation → "Füllmanager"

## Workflow

### Neuen Füllvorgang starten:

1. **Flaschenannahme**
   - Klicken Sie auf "Flasche annehmen"
   - Wählen Sie den Kunden aus
   - Wählen Sie die Flasche aus
   - Führen Sie die Prüfungen durch
   - Geben Sie die Füllparameter ein

2. **Füllung durchführen**
   - Nach der Annahme wird die Detailansicht geöffnet
   - Klicken Sie auf "Füllung starten"
   - Führen Sie die Füllung durch
   - Klicken Sie auf "Füllung beenden"
   - Geben Sie den tatsächlichen Enddruck ein

3. **Abschluss mit Unterschrift**
   - Nach dem Beenden erscheint die Unterschrifterfassung
   - Kunde unterschreibt im oberen Feld
   - Mitarbeiter unterschreibt im unteren Feld
   - Bestätigung ankreuzen
   - "Füllvorgang abschließen" klicken

4. **Beleg drucken**
   - Nach Abschluss kann der Beleg gedruckt werden
   - Automatische Druckansicht öffnet sich
   - Enthält alle Daten inkl. Unterschriften

## Technische Details

### Datenbank-Tabellen:
- `fuellmanager` - Haupttabelle für Füllvorgänge
- `fuellmanager_signaturen` - Digitale Unterschriften
- `fuellvorgang_erweitert` - Ereignisprotokoll

### API-Endpoints:
- `GET /fuellmanager/` - Übersicht
- `GET/POST /fuellmanager/neue-annahme` - Neue Annahme
- `GET /fuellmanager/details/<id>` - Details anzeigen
- `POST /fuellmanager/start-fuellung/<id>` - Füllung starten
- `POST /fuellmanager/beende-fuellung/<id>` - Füllung beenden
- `POST /fuellmanager/speichere-unterschrift/<id>` - Unterschriften speichern
- `GET /fuellmanager/drucken/<id>` - Druckansicht

### Touch-Optimierungen:
- Große Buttons (min. 60px Höhe)
- Touch-optimierte Unterschrifterfassung
- Responsive Design für Tablets
- Automatisches Neuladen bei aktiven Füllungen

## Sicherheit

- Alle Aktionen erfordern Anmeldung
- Operator wird automatisch erfasst
- IP-Adressen werden protokolliert
- Vollständige Ereignishistorie

## Wartung

### Logs einsehen:
```sql
SELECT * FROM fuellvorgang_erweitert 
WHERE fuellmanager_id = ? 
ORDER BY ereignis_zeit;
```

### Statistiken:
```sql
-- Tägliche Füllungen
SELECT DATE(erstellt_am) as datum, COUNT(*) as anzahl 
FROM fuellmanager 
WHERE status = 'abgeschlossen' 
GROUP BY DATE(erstellt_am);

-- Umsatz pro Tag
SELECT DATE(erstellt_am) as datum, SUM(gesamtpreis) as umsatz 
FROM fuellmanager 
WHERE status = 'abgeschlossen' 
GROUP BY DATE(erstellt_am);
```

## Troubleshooting

### Problem: Unterschrift wird nicht erfasst
- Browser-Kompatibilität prüfen (Chrome/Edge empfohlen)
- JavaScript-Konsole auf Fehler prüfen
- Canvas-Größe auf mobilen Geräten beachten

### Problem: Druckansicht funktioniert nicht
- Popup-Blocker deaktivieren
- Druckereinstellungen prüfen
- A4-Format einstellen

### Problem: Migration schlägt fehl
- Datenbank-Rechte prüfen
- Python-Umgebung aktiviert?
- Vorhandene Tabellen prüfen

## Erweiterungsmöglichkeiten

1. **QR-Code auf Beleg** für digitale Archivierung
2. **E-Mail-Versand** des Belegs an Kunden
3. **Statistik-Dashboard** für Füllmengen und Umsätze
4. **Barcode-Scanner** Integration für Flaschenauswahl
5. **Mehrsprachigkeit** für internationale Kunden
6. **SMS-Benachrichtigung** bei Fertigstellung

## Support

Bei Fragen oder Problemen wenden Sie sich an:
- Entwickler: [Ihr Name]
- E-Mail: [support@example.com]

---

*Füllmanager v1.0 - Teil des WartungsManager Systems*
