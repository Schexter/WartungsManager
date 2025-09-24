# TODO FAHRPLAN - FÜLLAUFTRAG ERWEITERT SYSTEM
## Erstellt von Hans Hahn - Alle Rechte vorbehalten

### Projektübersicht
- **Projekt**: Erweiterte Füllauftragsverwaltung mit Unterschriften
- **Zweck**: Komplette Dokumentation der Füllvorgänge mit Kundenverwaltung
- **Basis**: Vorhandenes Flaschen-Füllen System
- **Datum**: 03.07.2025

### PHASE 1: Datenbankstruktur erweitern ✅
- [x] Datenbank-Schema analysieren
- [x] Projektstruktur erstellen
- [x] Fahrplan definieren
- [ ] **Neue Tabellen erstellen**
  - [ ] fuellauftraege - Haupttabelle für Füllaufträge
  - [ ] fuellauftraege_details - Details zu Gasgemischen
  - [ ] kunden_unterschriften - Digitale Unterschriften
  - [ ] flaschenpruefungen - Prüfungshistorie

### PHASE 2: Backend-Erweiterungen
- [ ] **Datenmodelle entwickeln**
  - [ ] FuellauftragModel - Hauptauftrag mit Kunde
  - [ ] FuellauftragDetailModel - Gasgemisch und Preise
  - [ ] UnterschriftModel - Touch-Unterschriften
  - [ ] FlaschenpruefungModel - Prüfungsmanagement
  
- [ ] **Service Layer implementieren**
  - [ ] FuellauftragService - Auftragsverwaltung
  - [ ] UnterschriftService - Digitale Unterschriften
  - [ ] PruefungsService - Flaschenprüfungen
  - [ ] PreisberechnungService - Automatische Preise
  
- [ ] **API-Endpunkte entwickeln**
  - [ ] POST /api/fuellauftraege - Neuer Auftrag
  - [ ] PUT /api/fuellauftraege/{id}/unterschrift - Unterschrift hinzufügen
  - [ ] POST /api/fuellauftraege/{id}/pruefen - Flasche prüfen
  - [ ] GET /api/fuellauftraege/{id}/protokoll - Protokoll generieren

### PHASE 3: Frontend-Entwicklung
- [ ] **Unterschriftsfunktion**
  - [ ] Touch-Canvas für Unterschriften
  - [ ] Unterschrift-Pad für Tablets/Smartphones
  - [ ] Unterschrift-Validierung
  - [ ] Unterschrift-Speicherung als Base64
  
- [ ] **Prüfungsmanagement**
  - [ ] \"Flasche gecheckt\" Button
  - [ ] Prüfungshistorie anzeigen
  - [ ] Prüfungsprotokoll generieren
  - [ ] Prüfungsnotizen hinzufügen
  
- [ ] **Erweiterte Füllmaske**
  - [ ] Gasgemisch-Eingabe (O2, He, N2)
  - [ ] Automatische Preisberechnung
  - [ ] Volumen und Druckberechnung
  - [ ] Kostenaufschlüsselung

### PHASE 4: Integration mit Nitrox-Rechner
- [ ] **Berechnungs-Integration**
  - [ ] Gasgemisch-Berechnungen einbinden
  - [ ] MOD-Berechnung (Maximum Operating Depth)
  - [ ] EAD-Berechnung (Equivalent Air Depth)
  - [ ] Trimix-Berechnungen
  
- [ ] **Preiskalkulationen**
  - [ ] Helium-Preise (0,0950 € per Bar Ltr)
  - [ ] Sauerstoff-Preise (0,0100 € per Bar Ltr)
  - [ ] Luft-Preise (0,0020 € per Bar Ltr)
  - [ ] Gesamtpreisberechnung

### PHASE 5: Dokumentation und Protokolle
- [ ] **Füllprotokoll generieren**
  - [ ] PDF-Generierung mit Kundendaten
  - [ ] Gasgemisch-Details anzeigen
  - [ ] Unterschriften einbinden
  - [ ] Prüfungsvermerke hinzufügen
  
- [ ] **Druckfunktionen**
  - [ ] Etikettendruck für Flaschen
  - [ ] Füllprotokoll drucken
  - [ ] Kundenquittung generieren
  - [ ] Barcode-Etiketten erstellen

### PHASE 6: Testing und Optimierung
- [ ] **Touch-Interface Tests**
  - [ ] Unterschrift auf verschiedenen Geräten
  - [ ] Responsivität prüfen
  - [ ] Performance optimieren
  - [ ] Fehlerbehandlung testen
  
- [ ] **Datenbank-Performance**
  - [ ] Indizes für Füllaufträge
  - [ ] Archivierung alter Aufträge
  - [ ] Backup-Strategien
  - [ ] Datenintegrität prüfen

### TECHNISCHE SPEZIFIKATIONEN

#### Datenbank-Schema
```sql
-- Füllaufträge Haupttabelle
CREATE TABLE fuellauftraege (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kunden_id INTEGER NOT NULL,
    flaschen_id INTEGER NOT NULL,
    datum DATETIME NOT NULL,
    operator TEXT NOT NULL,
    
    -- Druckdaten
    restdruck_bar REAL NOT NULL,
    zieldruck_bar REAL NOT NULL,
    
    -- Gasgemisch
    sauerstoff_prozent REAL NOT NULL,
    helium_prozent REAL NOT NULL,
    stickstoff_prozent REAL NOT NULL,
    
    -- Berechnungen
    volumen_liter REAL NOT NULL,
    mod_1_2_bar REAL,
    mod_1_4_bar REAL,
    mod_1_6_bar REAL,
    end_30m REAL,
    
    -- Preise
    preis_helium_euro REAL NOT NULL,
    preis_sauerstoff_euro REAL NOT NULL,
    preis_luft_euro REAL NOT NULL,
    gesamtpreis_euro REAL NOT NULL,
    
    -- Status
    flasche_geprueft BOOLEAN DEFAULT 0,
    pruefung_datum DATETIME,
    pruefung_notizen TEXT,
    
    -- Unterschriften (Base64)
    mitarbeiter_unterschrift TEXT,
    kunden_unterschrift TEXT,
    
    -- Metadaten
    erstellt_am DATETIME DEFAULT CURRENT_TIMESTAMP,
    erstellt_von TEXT DEFAULT 'Hans Hahn'
);

-- Prüfungshistorie
CREATE TABLE flaschenpruefungen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fuellauftrag_id INTEGER NOT NULL,
    flaschen_id INTEGER NOT NULL,
    pruefung_datum DATETIME NOT NULL,
    pruefung_ergebnis TEXT NOT NULL,
    pruefung_notizen TEXT,
    pruefer TEXT NOT NULL,
    FOREIGN KEY (fuellauftrag_id) REFERENCES fuellauftraege(id)
);
```

#### Frontend-Komponenten
- **UnterschriftCanvas**: Touch-sensitive Unterschriftenfläche
- **FuellauftragForm**: Erweiterte Eingabemaske
- **PreisberechnerComponent**: Automatische Preiskalkulation
- **PruefungsButton**: Flasche als geprüft markieren
- **ProtokollGenerator**: PDF-Protokoll erstellen

#### API-Endpunkte
```python
# Neuer Füllauftrag
POST /api/fuellauftraege
{
    \"kunden_id\": 123,
    \"flaschen_id\": 456,
    \"restdruck_bar\": 0.0,
    \"zieldruck_bar\": 220.0,
    \"sauerstoff_prozent\": 34.0,
    \"helium_prozent\": 0.0,
    \"stickstoff_prozent\": 66.0,
    \"volumen_liter\": 24.0
}

# Unterschrift hinzufügen
PUT /api/fuellauftraege/{id}/unterschrift
{
    \"typ\": \"kunde\",
    \"unterschrift_base64\": \"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...\"
}

# Flasche prüfen
POST /api/fuellauftraege/{id}/pruefen
{
    \"pruefung_ergebnis\": \"OK\",
    \"pruefung_notizen\": \"Visuelle Prüfung erfolgreich\",
    \"pruefer\": \"Hans Hahn\"
}
```

### BENUTZERFREUNDLICHKEIT

#### Touch-Interface
- Große Buttons für Touch-Bedienung
- Unterschriftenfläche mit Finger/Stylus
- Responsive Design für Tablets
- Offline-Funktionalität

#### Workflows
1. **Füllauftrag erstellen**
   - Kunde auswählen/anlegen
   - Flasche scannen
   - Gasgemisch eingeben
   - Preise automatisch berechnen

2. **Flasche prüfen**
   - \"Flasche gecheckt\" Button
   - Prüfungsnotizen hinzufügen
   - Prüfungshistorie anzeigen

3. **Unterschriften sammeln**
   - Mitarbeiter unterschreibt
   - Kunde unterschreibt auf Tablet
   - Unterschriften in Auftrag speichern

4. **Protokoll generieren**
   - PDF mit allen Daten
   - Unterschriften eingebunden
   - Prüfungsvermerke enthalten

### SICHERHEIT UND COMPLIANCE
- Digitale Unterschriften rechtssicher
- Prüfungshistorie unveränderlich
- Audit-Trail für alle Änderungen
- Datenschutz-konform (DSGVO)

### PREISBERECHNUNG
Basierend auf Ihrem Screenshot:
- **Helium**: 0,0950 € pro Bar·Liter
- **Sauerstoff**: 0,0100 € pro Bar·Liter  
- **Luft**: 0,0020 € pro Bar·Liter
- **Beispielrechnung** (24L Flasche, 0→220 bar):
  - Sauerstoff (34%): 8,69 €
  - Luft (66%): 8,82 €
  - **Gesamtpreis: 17,51 €**

### NÄCHSTE SCHRITTE
1. **Datenbankstruktur erweitern**
2. **Backend-Services implementieren**
3. **Touch-Unterschriftenfunktion entwickeln**
4. **Prüfungsmanagement integrieren**
5. **PDF-Protokoll-Generator erstellen**
6. **Mobile-optimierte Oberfläche**

---
**Geschätzter Zeitaufwand:** 25-30 Stunden
**Priorität:** Hoch
**Abhängigkeiten:** Wartungsmanager-Hauptsystem, Kundenverwaltung
