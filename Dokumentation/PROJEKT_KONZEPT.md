# Wartungs- und Füllstandsmanagement-System

## 📋 Projektübersicht
**Ziel**: Netzwerkfähige Anwendung zur Verwaltung von Füllvorgängen, Wartungen und Betriebsstunden

## 🎯 Kernfunktionen

### Füllmanagement
- ✅ Beginn Füllen (Startzeit erfassen)
- ✅ Ende Füllen (Endzeit erfassen)
- ✅ Automatische Berechnung der Betriebsstunden seit SET
- ✅ Dokumentation aller Füllvorgänge

### Wartungsmanagement
- ✅ Filter gewechselt am: [Datum] durch: [Person]
- ✅ Öl getestet am: [Datum] durch: [Person]
- ✅ Countdown bis nächste Wartung
- ✅ Automatische Erinnerungen

### Protokoll & Dokumentation
- ✅ Handbefüllung Molekular- und Kohlefilter
- ✅ Etiketten-Druck mit genauen Werten
- ✅ Wann und von wem befüllt
- ✅ PDF-Export für Compliance

## 🌐 Netzwerk-Implementierung

### Option 1: Web-Anwendung (EMPFOHLEN)
**Frontend**: React/Vue.js + moderne UI
**Backend**: ASP.NET Core Web API
**Datenbank**: SQLite/SQL Server Express
**Hosting**: IIS oder selbst-gehosteter Kestrel Server
**IP**: Statische IP im lokalen Netzwerk

### Option 2: Desktop + API
**Client**: WPF/WinUI Anwendung
**Server**: Web API für Datenbank-Zugriff
**Synchronisation**: Über REST API

## 💾 Datenbank-Design

### Tabellen:
1. **Füllvorgänge** (FuellID, StartZeit, EndZeit, Dauer, Operator)
2. **Wartungen** (WartungsID, Typ, Datum, Durchgeführt_Von, Nächste_Fällig)
3. **Handbefüllungen** (BefuellID, Material, Datum, Operator, Menge)
4. **Betriebsstunden** (SET_Datum, Gesamt_Stunden, Aktuelle_Periode)
5. **Einstellungen** (Parameter, Wert, Beschreibung)

## 🔧 Technologie-Stack

### Backend
- **ASP.NET Core 8** (Cross-Platform, Modern)
- **Entity Framework Core** (ORM für Datenbank)
- **SQLite** (Initial) → **SQL Server Express** (Skalierung)
- **AutoMapper** (Object Mapping)
- **Serilog** (Strukturiertes Logging)

### Frontend
- **Blazor Server/WASM** oder **React**
- **Bootstrap** oder **Material Design**
- **Chart.js** für Diagramme
- **PrintJS** für Etikett-Druck

### Zusätzliche Tools
- **Barcode/QR-Generator** für Etiketten
- **PDF Generation** (iTextSharp/PuppeteerSharp)
- **Task Scheduler** für automatische Wartungserinnerungen

## 🚀 Erweiterte Ideen

### Zusätzliche Features
1. **Dashboard mit Live-Status**
   - Aktuelle Füllvorgänge
   - Wartungsstatus-Ampel
   - Trend-Diagramme

2. **Benutzerrechte-System**
   - Operator: Nur Füllung starten/stoppen
   - Techniker: Wartungen eintragen
   - Admin: Alle Funktionen + Einstellungen

3. **Automatisierung**
   - Email-Benachrichtigungen bei Wartung fällig
   - Automatische Backup-Erstellung
   - Export-Scheduler für Berichte

4. **Mobile Unterstützung**
   - Responsive Web-Design
   - QR-Code Scanner für Equipment

5. **Reporting & Analytics**
   - Füllzyklen-Analyse
   - Wartungskosten-Tracking
   - Effizienz-Kennzahlen
   - Compliance-Berichte

6. **Integration**
   - Barcode-Scanner Integration
   - RFID-Tags für Equipment
   - Excel Import/Export
   - Drucker-Integration für Etiketten

## 🎨 UI/UX Konzept

### Hauptbildschirm
```
[LOGO] Wartungsmanager Pro                    [Benutzer: Max] [Logout]

┌─────────────────┬─────────────────┬─────────────────┐
│   FÜLLUNG       │    WARTUNG      │   PROTOKOLL     │
├─────────────────┼─────────────────┼─────────────────┤
│ 🟢 START FÜLLUNG│ 📅 Nächste:    │ 📄 Handbefüllung│
│ 🔴 STOP FÜLLUNG │    Filter: 5T   │ 🖨️ Etiketten    │
│                 │    Öl: 12T      │ 📊 Berichte     │
│ ⏱️ Aktuell:     │                 │                 │
│   2h 30min      │ 🔧 Wartung      │                 │
│                 │    eintragen    │                 │
│ 📈 Gesamt:      │                 │                 │
│   1.247h        │                 │                 │
└─────────────────┴─────────────────┴─────────────────┘

STATUS: Normalbetrieb ✅    |    NETZWERK: 192.168.1.100 🌐
```

## 🔌 Sensorik-Vorbereitung

### Geplante Sensoren
- **Füllstand-Sensoren** (Ultraschall/Kapazitiv)
- **Drucksensoren** für Systemüberwachung
- **Temperatursensoren** für Betriebstemperatur
- **Durchflussmesser** für Präzise Mengenerfassung

### Integration
- **Modbus/RS485** für industrielle Sensoren
- **Arduino/Raspberry Pi** als Gateway
- **MQTT** für IoT-Kommunikation
- **REST API** für Sensor-Datenübertragung

## 🏗️ Entwicklungsphasen

### Phase 1: Basis-System (4-6 Wochen)
- Datenbank-Design & Implementation
- Grundlegende UI
- Füll-Start/Stop Funktionalität
- Basis-Wartungsmanagement

### Phase 2: Erweiterte Features (3-4 Wochen)
- Handbefüllung-Protokoll
- Etiketten-Druck
- Berichtswesen
- Benutzerrechte

### Phase 3: Automatisierung (2-3 Wochen)
- Email-Benachrichtigungen
- Automatische Berichte
- Mobile Optimierung

### Phase 4: Sensorik (Zukünftig)
- Hardware-Integration
- Automatische Datenerfassung
- Predictive Maintenance

## 📁 Projekt-Struktur
```
WartungsManager/
├── 📄 Dokumentation/
├── 🏗️ Source/
│   ├── Backend/
│   ├── Frontend/
│   └── Database/
├── 🧪 Tests/
├── 📦 Deployment/
└── 📋 Docs/
```
