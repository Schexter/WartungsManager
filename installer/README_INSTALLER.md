# 🚀 WARTUNGSMANAGER - VOLLAUTOMATISCHER INSTALLER
**Version:** 1.0  
**Datum:** 26.06.2025  
**Zielrechner:** Kassenrechner (Server-Modus)

## 🎯 **WAS DIESER INSTALLER MACHT**

### **✅ Vollautomatische Installation:**
- **Python Portable** - Download und Installation
- **Wartungsmanager** - Komplett eingerichtet
- **Desktop-Icon** - 1-Klick-Start
- **Auto-Start** - Startet mit Windows
- **NAS-Backup** - Zur WD My Cloud (192.168.0.231)
- **Firewall** - Port 5000 automatisch freigegeben

### **✅ Nach der Installation verfügbar:**
- **Desktop:** "Wartungsmanager.bat" - Doppelklick startet alles
- **Browser:** http://localhost:5000 - Direkt im Browser öffnen
- **Netzwerk:** http://[PC-IP]:5000 - Von anderen Geräten erreichbar
- **iPad:** Funktioniert popup-frei und touch-optimiert

---

## 🔧 **INSTALLATION**

### **Schritt 1: Administrator-Rechte**
```
Rechtsklick auf "setup_wartungsmanager.bat"
→ "Als Administrator ausführen"
→ UAC-Dialog bestätigen
```

### **Schritt 2: Automatische Installation**
```
✅ Der Installer macht ALLES automatisch:
   - Python Installation (falls nicht vorhanden)
   - Wartungsmanager Setup
   - Desktop-Icon erstellen
   - Auto-Start konfigurieren
   - NAS-Backup einrichten
   - Firewall konfigurieren
```

### **Schritt 3: Fertig!**
```
Nach ca. 2-5 Minuten:
✅ Wartungsmanager ist installiert
✅ Desktop-Icon ist verfügbar
✅ Auto-Start ist konfiguriert
✅ System ist bereit
```

---

## 🖥️ **BEDIENUNG NACH INSTALLATION**

### **Wartungsmanager starten:**
1. **Doppelklick** auf Desktop-Icon "Wartungsmanager.bat"
2. **Server startet** automatisch
3. **Browser öffnet** http://localhost:5000 automatisch
4. **Sofort einsatzbereit**

### **Von anderen Geräten zugreifen:**
- **iPad:** Browser → http://[KASSENRECHNER-IP]:5000
- **Andere PCs:** Browser → http://[KASSENRECHNER-IP]:5000
- **Touch-optimiert:** iPad-Modus automatisch erkannt

---

## 💾 **BACKUP-SYSTEM**

### **Automatische NAS-Backups:**
- **Ziel:** \\192.168.0.231\Tauchen\KompressorUeberwachung\backup
- **Intervall:** Alle 6 Stunden automatisch
- **Inhalt:** Datenbank, Logs, Konfiguration
- **Zeitstempel:** Jedes Backup eindeutig benannt

### **Manuelles Backup:**
```
Doppelklick auf: C:\Wartungsmanager\backup_to_nas.bat
```

---

## ⚙️ **SYSTEM-INTEGRATION**

### **Auto-Start:**
- Startet **automatisch mit Windows** (30s Verzögerung)
- Läuft **im Hintergrund** als Service
- **Immer verfügbar** ohne manuelle Aktivierung

### **Firewall:**
- **Port 5000** automatisch freigegeben
- **Netzwerk-Zugriff** von allen Geräten möglich
- **Sicher konfiguriert** nur für notwendige Ports

### **Windows-Integration:**
- **Desktop-Icon** für einfachen Start
- **Startmenü-Einträge** in Programme
- **Task Scheduler** für automatische Backups

---

## 🔧 **TROUBLESHOOTING**

### **Installation schlägt fehl:**
```
Lösung:
1. Als Administrator ausführen
2. Antivirus temporär deaktivieren
3. Internet-Verbindung prüfen (für Python-Download)
```

### **Server startet nicht:**
```
Lösung:
1. Windows-Firewall prüfen
2. Port 5000 bereits belegt? → Anderen Port verwenden
3. Python-Installation prüfen
```

### **NAS-Backup funktioniert nicht:**
```
Lösung:
1. NAS-Verbindung testen: \\192.168.0.231\Tauchen
2. Ordner-Berechtigung prüfen
3. Backup-Script manuell ausführen
```

---

## 🗑️ **DEINSTALLATION**

### **Vollständige Entfernung:**
```
Doppelklick auf: C:\Wartungsmanager\uninstall.bat
→ Alles wird sauber entfernt:
   - Programm-Dateien
   - Desktop-Icons
   - Auto-Start
   - Firewall-Regeln
   - Task Scheduler
```

---

## 📋 **SYSTEM-ANFORDERUNGEN**

### **Minimal:**
- **Windows 10/11** (64-bit)
- **2 GB RAM** (4 GB empfohlen)
- **500 MB Festplatte** für Installation
- **Netzwerk-Verbindung** zur NAS (optional)
- **Administrator-Rechte** für Installation

### **Empfohlen:**
- **Touch-Display** für optimale Bedienung
- **SSD-Festplatte** für bessere Performance
- **Gigabit-Netzwerk** für schnelle NAS-Backups

---

## 🎯 **NACH DER INSTALLATION**

### **✅ Sie haben dann:**
- **Wartungsmanager läuft lokal** auf Kassenrechner
- **Desktop-Icon** für 1-Klick-Start
- **Auto-Start** mit Windows
- **NAS-Backup** alle 6 Stunden
- **iPad-Zugriff** popup-frei und touch-optimiert
- **Multi-Client** - mehrere Benutzer gleichzeitig
- **Wartungsfrei** - läuft automatisch

### **✅ Alle Geräte können zugreifen:**
- **Kassenrechner:** http://localhost:5000
- **iPad:** http://[KASSENRECHNER-IP]:5000  
- **Andere PCs:** http://[KASSENRECHNER-IP]:5000

---

**🚀 BEREIT FÜR 1-KLICK-INSTALLATION!**

**Einfach "setup_wartungsmanager.bat" als Administrator ausführen!**
