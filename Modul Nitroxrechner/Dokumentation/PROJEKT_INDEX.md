# PROJEKT INDEX - NITROXRECHNER MODUL
## Erstellt von Hans Hahn - Alle Rechte vorbehalten

### Projektinformationen
- **Projektname**: Nitroxrechner Modul
- **Version**: 1.0.0
- **Erstellt**: 03.07.2025
- **Entwickler**: Hans Hahn
- **Lizenz**: Alle Rechte vorbehalten

### Projektbeschreibung
Das Nitroxrechner Modul erweitert den bestehenden Wartungsmanager um professionelle Gasberechnungsfunktionen für Nitrox und Trimix. Es bietet eine nahtlose Integration in das bestehende Dashboard und ermöglicht präzise Berechnungen für Tauchgasgemische.

### Verzeichnisstruktur
```
Modul Nitroxrechner/
├── Source/
│   └── Python/
│       ├── models/           # Datenmodelle
│       ├── routes/           # API-Endpunkte
│       ├── services/         # Geschäftslogik
│       └── templates/        # HTML-Templates
├── Dokumentation/
│   ├── TODO_FAHRPLAN_NITROXRECHNER.md
│   ├── PROJEKT_INDEX.md
│   └── API_DOKUMENTATION.md
├── Logs/
│   └── error.log
├── Chats/
│   └── chat_sessions/
└── TRIMIX Fuellen Peter_2022_06_29.xlsx
```

### Kernfunktionalitäten
1. **Nitrox-Berechnungen**
   - Sauerstoffanteil-Berechnung
   - Maximum Operating Depth (MOD)
   - Equivalent Air Depth (EAD)
   - Partial Pressure Blending

2. **Trimix-Berechnungen**
   - Helium/Stickstoff/Sauerstoff-Mischung
   - Narcotic Depth berechnen
   - Equivalent Narcotic Depth (END)
   - Optimale Gasmischung

3. **Dashboard-Integration**
   - Eigene Kachel im Hauptdashboard
   - Schnellzugriff auf Berechnungen
   - Berechnungshistorie
   - Export-Funktionen

### Technische Spezifikationen
- **Backend**: Python 3.11+, Flask Framework
- **Database**: SQLite (wartungsmanager.db)
- **Frontend**: HTML5, CSS3, JavaScript
- **Integration**: Wartungsmanager-Architektur
- **Design**: Touch-optimiert, responsive

### Datenbank-Schema
```sql
-- Gasberechnungen
CREATE TABLE gasberechnungen (
    id INTEGER PRIMARY KEY,
    berechnung_typ TEXT NOT NULL,
    eingabe_parameter TEXT NOT NULL,
    ergebnis TEXT NOT NULL,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    erstellt_von TEXT
);

-- Favoriten-Mischungen
CREATE TABLE favoriten_mischungen (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    o2_anteil REAL NOT NULL,
    he_anteil REAL DEFAULT 0,
    n2_anteil REAL NOT NULL,
    mod_tiefe REAL,
    notizen TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### API-Endpunkte
- `GET /nitroxrechner/` - Hauptseite
- `POST /nitroxrechner/berechnen` - Gasberechnung
- `GET /nitroxrechner/historie` - Berechnungshistorie
- `POST /nitroxrechner/favoriten` - Favoriten speichern
- `GET /nitroxrechner/export` - Export-Funktionen

### Sicherheitsfeatures
- Eingabevalidierung für alle Parameter
- Sichere Gasberechnungsalgorithmen
- Fehlerbehandlung und Logging
- Audit-Trail für alle Berechnungen

### Performance-Optimierungen
- Caching für häufige Berechnungen
- Optimierte Datenbankzugriffe
- Asynchrone Berechnungen
- Responsive Design

### Qualitätssicherung
- Unit Tests für alle Berechnungen
- Integration Tests
- Code-Review-Prozess
- Automatisierte Tests

### Deployment-Informationen
- Integration in bestehende Wartungsmanager-Installation
- Keine separaten Abhängigkeiten
- Automatische Datenbankmigrationen
- Rollback-Unterstützung

### Wartung und Support
- Logging in `Logs/error.log`
- Automatische Backups
- Update-Mechanismen
- Monitoring-Integration

### Lizenz und Rechte
- **Copyright**: Hans Hahn
- **Lizenz**: Alle Rechte vorbehalten
- **Verwendung**: Nur mit ausdrücklicher Genehmigung

### Kontaktinformationen
- **Entwickler**: Hans Hahn
- **Projekt**: Wartungsmanager Integration
- **Version**: 1.0.0
- **Status**: In Entwicklung

---
**Letzte Aktualisierung**: 03.07.2025
**Nächste Review**: Bei Milestone-Erreichen
