# TODO: Bulk-Anwendung Verbesserungen
**Erstellt:** 26.06.2025  
**Priorität:** Hoch  
**Geschätzte Arbeitszeit:** 4-6 Stunden  

## 🎯 **Hauptziele:**
- [x] Projektanalyse abgeschlossen
- [ ] Leere Flaschen Funktionalität implementieren
- [ ] Bulk zu "Flaschen Füllen" umbenennen
- [ ] Checkbox-System für Flaschenauswahl
- [ ] Füller und Enddruck-Speicherung

---

## 📋 **Detaillierte Aufgaben:**

### **Phase 1: Frontend Verbesserungen (2-3h)**
- [ ] **1.1** bulk_fuelling.html umbenennen zu flaschen_fuellen.html
- [ ] **1.2** Alle "Bulk" Texte zu "Flaschen Füllen" ändern
- [ ] **1.3** Button "Leere Flaschen annehmen" hinzufügen
- [ ] **1.4** Checkbox-System für Flaschenauswahl implementieren
- [ ] **1.5** Füller und Enddruck Eingabefelder hinzufügen
- [ ] **1.6** JavaScript für neue Funktionalitäten

### **Phase 2: Backend Anpassungen (1-2h)**
- [ ] **2.1** Route für leere Flaschen ohne Kompressor-Check
- [ ] **2.2** Service für Flaschenauswahl mit Checkboxen
- [ ] **2.3** Füller und Enddruck in Datenmodell erweitern
- [ ] **2.4** API-Endpunkte anpassen/erweitern

### **Phase 3: Datenbank & Services (1h)**
- [ ] **3.1** Datenmodell prüfen/erweitern für neue Felder
- [ ] **3.2** Migration erstellen falls nötig
- [ ] **3.3** Services aktualisieren

### **Phase 4: Testing & Dokumentation (1h)**
- [ ] **4.1** Funktionalitäten testen
- [ ] **4.2** Dokumentation aktualisieren
- [ ] **4.3** Chat-Protokoll vervollständigen

---

## 🔧 **Technische Notizen:**
- Vorhandene Bulk-Struktur beibehalten, nur erweitern
- Checkbox-State in JavaScript verwalten
- Kompressor-Check optional machen für leere Flaschen
- Füller und Enddruck in FlascheFuellvorgang Modell

## ⚠️ **Wichtige Hinweise:**
- Keine neuen Skripte erstellen, vorhandene erweitern
- Ordentliche Klassenstruktur beibehalten
- Log-Datei für alle Änderungen
- Spaghetti-Code vermeiden

## 📁 **Betroffene Dateien:**
- `app/templates/bulk_fuelling.html` → umbenennen
- `app/routes/kompressor_api.py` - erweitern
- `app/models/bulk_fuelling.py` - prüfen/erweitern
- `app/services/bulk_fuelling_service.py` - erweitern
- Routing in main.py anpassen

---
**Status:** 🔄 In Bearbeitung  
**Nächster Schritt:** Phase 1.1 - Template umbenennen
