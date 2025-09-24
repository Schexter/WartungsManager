# TODO: Kompressor-System Erweiterung

## **FAHRPLAN für die Umsetzung**

### **Phase 1: Datenbank-Modelle erstellen** ✅ ABGESCHLOSSEN
- [x] 1.1 Kompressor-Betriebsstunden Modell (mit Öl-Tests)
- [x] 1.2 Kunden/Mitglieder Modell
- [x] 1.3 Flaschen Modell
- [x] 1.4 Bulk-Füllvorgang Modell
- [x] 1.5 Datenbank-Migration erstellen

### **Phase 2: Backend-Logik erweitern** ✅ ABGESCHLOSSEN
- [x] 2.1 Kompressor An/Aus Service-Klassen
- [x] 2.2 Bulk-Füllvorgang Service
- [x] 2.3 Kunden-Management Service
- [x] 2.4 Flaschen-Management Service
- [x] 2.5 API-Routen erweitern

### **Phase 3: Frontend/UI entwickeln** ✅ AKTUELL
- [x] 3.1 Kompressor-Steuerung UI (An/Aus Buttons) ✅ ABGESCHLOSSEN
- [x] 3.2 Öl-Test Pop-up ✅ INTEGRIERT in 3.1
- [x] 3.3 Bulk-Füllvorgang Interface ✅ ABGESCHLOSSEN
- [x] 3.4 **Kompressor-Reset & Wartungsintervall-System** ✅ VOLLSTÄNDIG ABGESCHLOSSEN
  - [x] Backend-Service: `kompressor_reset_passwortgeschuetzt()`
  - [x] API-Endpunkt: `POST /api/kompressor/reset`
  - [x] Wartungsintervall-Model: `Wartungsintervall`
  - [x] Wartungsintervall-Service: `WartungsintervallService`
  - [x] Wartungsintervall-API: `/api/kompressor/wartungsintervall/*`
  - [x] Gesamt-Stunden-Korrektur: `/api/kompressor/gesamt-betriebszeit/korrigieren`
  - [x] Frontend-Buttons: Wartungsinterface mit drei Reset-Funktionen
  - [x] Timer-Bug behoben: Startet jetzt bei 00:00:00
  - [x] Drei-Ebenen-System: Laufzeit / Wartungsintervall / Gesamt-Betriebszeit
  - [x] Passwort-Schutz: Magicfactory15!
  - [x] Audit-Trail: Vollständige Protokollierung
  - [x] Reparatur-Tools: fix_kompressor_issues.py + KOMPRESSOR_REPARATUR.bat
  - [x] Migration: Wartungsintervall-Tabelle
- [ ] 3.5 Kunden-Verwaltung UI ← NÄCHSTER SCHRITT
- [ ] 3.6 Flaschen-Verwaltung UI

### **Phase 4: Integration & Testing**
- [ ] 4.1 Alle Komponenten zusammenführen
- [ ] 4.2 Datenbankverbindungen testen
- [ ] 4.3 UI-Tests durchführen
- [ ] 4.4 Fehlerbehandlung implementieren

### **Phase 5: Deployment & Dokumentation**
- [ ] 5.1 System dokumentieren
- [ ] 5.2 Benutzerhandbuch erstellen
- [ ] 5.3 Deployment-Anweisungen

## **TECHNISCHE ANFORDERUNGEN**

### **Neue Funktionen:**
1. **Kompressor-Steuerung:**
   - Button "Kompressor AN" → Betriebsstunden-Tracking startet
   - Button "Kompressor AUS" → Betriebsstunden-Tracking stoppt
   - Öl-Test Pop-up bei "AN" → Wer testet? Ergebnis OK/NOK
   - Daten in DB speichern

2. **Bulk-Füllvorgang:**
   - Mehrere Flaschen gleichzeitig
   - Flaschennummern + Besitzer eingeben
   - Flaschen vorher registrieren, später nur anhaken
   - Automatische Kundenanlage

3. **Kundenverwaltung:**
   - Automatische Erkennung (existiert bereits?)
   - Mitgliedsnummern-System
   - Kundenanlage bei Bedarf

4. **Kompressor-Reset (WARTUNG):**
   - Passwortgeschützter Reset auf 00:00:00
   - Passwort: Magicfactory15!
   - API-Endpunkt: POST /api/kompressor/reset
   - Vollständige Protokollierung aller Resets
   - Audit-Trail mit alter Laufzeit

### **Datenbank-Schema:**
- `kompressor_betrieb` - Betriebsstunden, Öl-Tests
- `kunden` - Kundendaten, Mitgliedsnummern
- `flaschen` - Flaschen-Registry
- `bulk_fuellvorgaenge` - Bulk-Füllungen
- `flasche_fuellvorgang` - Many-to-Many Relation

## **AKTUELLE PRIORITÄT:**
**Phase 2 abgeschlossen! Starte mit Phase 3.1 - Kompressor-Steuerung UI**

---
**Erstellt:** 2025-06-26
**Letztes Update:** 2025-06-26 12:15
**Status:** Phase 3.4 Kompressor-Reset ABGESCHLOSSEN! ✅ 
Phase 3.5 Kunden-Verwaltung UI als nächstes
**Nächster Schritt:** Kunden-Verwaltung UI implementieren (CRUD-Interface für Kunden)

## **🔄 NEUE FUNKTIONALITÄT - KOMPRESSOR RESET**
**Implementiert:** 26.06.2025
- ✅ Passwortgeschützter Reset (Magicfactory15!)
- ✅ API-Endpunkt `/api/kompressor/reset`
- ✅ Vollständige Audit-Spur
- ✅ Sichere Passwort-Validierung
- ✅ Reset setzt Kompressor-Timer auf 00:00:00
- ✅ Dokumentation in `Logs/kompressor_reset_implementation_2025-06-26.md`
