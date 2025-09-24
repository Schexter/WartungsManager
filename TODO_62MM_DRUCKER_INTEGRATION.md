# 🖨️ TODO: 62mm Drucker Integration - Patronenwechsel

## 📋 Aufgabe: Thermodrucker für Patronen-Etiketten

**Projekt:** WartungsManager - Patronenwechsel 62mm Drucker-Modul  
**Erstellt:** 26.06.2025  
**Status:** 🚀 Geplant  
**Priorität:** ⭐ Hoch (Bestehende Funktion erweitern)  
**Kontext:** ✅ Patronenwechsel-System bereits komplett implementiert  

---

## 🎯 Ziel:
**62mm Thermodrucker** für Patronen-Kennzeichnung ins bestehende System integrieren:
- ✅ Molekularsieb Patrone 1 & 2 Etiketten
- ✅ Kohle-Filter Etiketten  
- ✅ QR-Code mit Wartungslink
- ✅ Offline-Druckwarteschlange
- ✅ **Wiederholbare Ausdrucke** für nachträglichen Druck

---

## 📦 Technologie-Erweiterungen:

### Neue Dependencies (requirements.txt):
```python
# 62mm Thermodrucker Support
python-escpos==3.0a9    # ESC/POS Thermodrucker-Treiber
qrcode==7.4.2           # QR-Code Generierung
Pillow==10.0.1          # Bildverarbeitung (bereits vorhanden in reportlab)
```

### Bestehende Integration:
- ✅ **reportlab** (bereits vorhanden) - für PDF-Backup
- ✅ **Flask/SQLAlchemy** (bereits vorhanden) - Web-Integration
- ✅ **Patronenwechsel-Model** (bereits implementiert)

---

## 🏗️ Entwicklungsschritte:

### Phase 1: Basis-Druckfunktionalität (2-3 Tage)

#### 1.1 Dependencies installieren
```bash
cd C:\SoftwareProjekte\WartungsManager\Source\Python
python -m pip install python-escpos==3.0a9 qrcode==7.4.2
```

#### 1.2 Print Service erstellen
**Datei:** `app/services/print_service.py`
- ESC/POS Drucker-Klasse
- 62mm Layout-Templates
- QR-Code Generierung
- Druckwarteschlange-Management

#### 1.3 Print Model erweitern  
**Datei:** `app/models/print_jobs.py`
- Druckjob-Verwaltung (für Wiederholung)
- Drucker-Konfiguration
- Print-Status Tracking

#### 1.4 API-Routes erweitern
**Datei:** `app/routes/patronenwechsel.py`
- `/patronenwechsel/print/<int:wechsel_id>` - Etikett drucken
- `/patronenwechsel/print/reprint/<int:job_id>` - Wiederholungsdruck
- `/patronenwechsel/print/queue` - Warteschlange-Status

### Phase 2: UI-Integration (1-2 Tage)

#### 2.1 Template erweitern
**Datei:** `app/templates/patronenwechsel/index.html`
- "Etiketten drucken" Button zu Historie hinzufügen
- Print-Status Anzeige
- Reprint-Funktionalität

#### 2.2 JavaScript erweitern
- `printPatronenEtikett(wechselId)` Funktion
- `reprintEtikett(jobId)` Funktion  
- Print-Status Updates

### Phase 3: Erweiterte Features (1-2 Tage)

#### 3.1 Print-Templates
- **Molekularsieb-Etikett** (62mm x 40mm)
- **Kohle-Filter-Etikett** (62mm x 30mm)
- **QR-Code Integration** (Link zu Wartungsdetails)

#### 3.2 Offline-Funktionalität
- Druckwarteschlange bei Drucker offline
- Automatischer Retry bei Drucker online
- Batch-Druck für mehrere Jobs

---

## 📄 Etikett-Layout (62mm Breite):

```
╔════════════════════════════════════════════════════════════╗
║                    WARTUNGSMANAGER                        ║
║                                                            ║
║  Patronenwechsel: 26.06.2025 14:30                        ║
║  Betriebsstunden: 1.247,5h                                ║
║  ───────────────────────────────────────────────────────  ║
║  MOLEKULARSIEB PATRONE 1                                   ║
║  Charge: MS2025-06-A47                                     ║
║  Eingebaut: Max Mustermann                                 ║
║  ───────────────────────────────────────────────────────  ║
║  Nächster Wechsel: ca. 1.259,5h                          ║
║                                                            ║
║              [QR-CODE]                                     ║
║                                                            ║
║  wartungsmanager.local/patronenwechsel/123                 ║
╚════════════════════════════════════════════════════════════╝
```

---

## 🔌 Hardware-Integration:

### ESC/POS Drucker-Konfiguration:
```python
# Beispiel-Konfiguration für gängige 62mm Drucker
PRINTER_CONFIG = {
    'interface': 'usb',        # USB, Serial, Network
    'vendor_id': 0x04b8,       # Epson TM-T20II
    'product_id': 0x0202,
    'profile': 'TM-T20',
    'encoding': 'cp850'        # Deutsche Umlaute
}
```

### Unterstützte Drucker:
- ✅ **Epson TM-T20II** (USB/Ethernet)
- ✅ **Star TSP143III** (USB/Bluetooth)
- ✅ **Generic ESC/POS** (58mm/62mm/80mm)

---

## 🔗 Integration ins bestehende System:

### Patronenwechsel-Service erweitern:
```python
# In patronenwechsel_service.py
def patronenwechsel_durchfuehren(...):
    # ... bestehender Code ...
    
    # NEU: Automatischer Druck nach Wechsel
    if print_etiketten:
        print_service.print_patronenwechsel_etiketten(neuer_wechsel.id)
    
    return result
```

### API-Routes erweitern:
```python
# In routes/patronenwechsel.py
@bp.route('/api/print/<int:wechsel_id>')
def print_etiketten(wechsel_id):
    # Etiketten für spezifischen Wechsel drucken
    pass

@bp.route('/api/reprint/<int:job_id>')  
def reprint_etikett(job_id):
    # Wiederholungsdruck aus Historie
    pass
```

---

## 🧪 Testing-Plan:

### 1. Drucker-Tests:
- ✅ USB-Verbindung erkennen
- ✅ Testausdruck (Alignment)
- ✅ Etikett-Format validieren
- ✅ QR-Code Lesbarkeit

### 2. System-Tests:
- ✅ Integration mit Patronenwechsel
- ✅ Offline-Warteschlange
- ✅ Wiederholungsdruck
- ✅ Error-Handling

### 3. UI-Tests:
- ✅ Touch-Bedienung
- ✅ Print-Status Updates
- ✅ Responsive Layout

---

## 📝 Deliverables:

### Code-Files:
1. ✅ `app/services/print_service.py` - Hauptklasse
2. ✅ `app/models/print_jobs.py` - Datenmodell  
3. ✅ Erweiterte API in `routes/patronenwechsel.py`
4. ✅ UI-Updates in `templates/patronenwechsel/index.html`
5. ✅ Aktualisierte `requirements.txt`

### Dokumentation:
1. ✅ `DRUCKER_SETUP.md` - Hardware-Konfiguration
2. ✅ `PRINT_TEMPLATES.md` - Etikett-Formate
3. ✅ Logs in `Logs/error.log` für Debug

### Testing:
1. ✅ `tests/test_print_service.py` - Unit Tests
2. ✅ `tests/test_patronenwechsel_print.py` - Integration Tests

---

## ⚠️ Wichtige Hinweise:

### Sicherheit:
- 🔒 **Passwort-geschützter** Wiederholungsdruck
- 🔒 **Audit-Log** für alle Druckjobs
- 🔒 **Drucker-Zugriffskontrolle**

### Performance:
- ⚡ **Asynchroner Druck** (nicht UI blockieren)
- ⚡ **Batch-Processing** für mehrere Etiketten
- ⚡ **Cache** für QR-Code Generierung

### Wartung:
- 🔧 **Drucker-Status** Monitoring
- 🔧 **Papier-Ende** Erkennung
- 🔧 **Error-Recovery** bei Verbindungsproblemen

---

## 🚀 Nächste Schritte:
1. **[SOFORT]** Dependencies installieren
2. **[TAG 1]** `print_service.py` implementieren  
3. **[TAG 2]** API-Integration & Testing
4. **[TAG 3]** UI-Integration & finale Tests

---

**Geschätzte Entwicklungszeit:** 4-6 Tage  
**Tester:** Nach jeder Phase mit echtem 62mm Drucker  
**Deployment:** Nach erfolgreichem Hardware-Test  

---
*Erstellt: 26.06.2025 | Korrigiert: 62mm (nicht 62cm!) | Status: Bereit zur Implementierung*