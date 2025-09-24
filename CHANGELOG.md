# CHANGELOG - WartungsManager v3.1

## [2025-09-23] Bug-Fixes und Shelly-Integration verbessert

### Durchgeführt:
- **base.html Template-Fehler behoben**: HTML-Kommentare durch Jinja2-Kommentare ersetzt für nicht implementierte Routen
  - `main.fuell_center` Route-Referenz korrigiert
  - `main.kundenmanager` Route-Referenz korrigiert
  - `main.flaschen_annehmen` Route-Referenz korrigiert
  - `main.bulk_fuelling` Route-Referenz korrigiert
  - `main.pruefungsmanagement` Route-Referenz korrigiert

- **Shelly IoT-Modul erweitert**:
  - Neues shelly.html Template erstellt mit Debug-Funktionalität
  - Verbesserte Netzwerk-Erkennung mit Port-Scan (80 und 8080)
  - Erweiterte Shelly-Device-Erkennung für Gen1 und Gen2/Plus Geräte
  - Detailliertes Logging und Fehleranalyse hinzugefügt
  - Progress-Tracking beim Netzwerk-Scan

### Funktioniert:
- Dashboard lädt ohne Fehler
- Shelly-Setup-Seite (/shelly-setup) ist erreichbar
- Shelly-Verwaltungsseite (/shelly) funktioniert mit Debug-Informationen
- Netzwerk-Scanner zeigt detaillierte Informationen
- Template-Engine wirft keine Fehler mehr bei auskommentierten Links

### Nächste Schritte:
- Testen der Shelly-Erkennung im realen Netzwerk
- Prüfung der tatsächlichen Shelly-IPs und Ports
- Ggf. erweiterte Authentifizierung für Shelly-Geräte implementieren
- Performance-Optimierung des Netzwerk-Scanners

### Probleme/Notizen:
- Shelly-Geräte werden möglicherweise nicht gefunden, wenn:
  - Sie in einem anderen Netzwerk-Segment sind
  - Sie andere Ports als 80/8080 verwenden
  - Eine Firewall die Kommunikation blockiert
  - Sie ausgeschaltet sind

### Debug-Hinweise:
- Console-Output im Browser prüfen (F12 -> Console)
- Server-Logs beachten für [SHELLY] Meldungen
- Debug-Info-Box auf der Shelly-Seite zeigt alle Scan-Details

---

**Erstellt von Hans Hahn - Alle Rechte vorbehalten**
