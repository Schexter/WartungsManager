# 🏢 NAS-DEPLOYMENT GUIDE: Wartungsmanager
**Datum:** 26.06.2025  
**Ziel:** Wartungsmanager auf NAS hosten, von Kasse/iPad ohne Python nutzen

## 🎯 **ÜBERSICHT**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      NAS        │    │     KASSE       │    │     IPAD        │
│  (Flask Server) │◄───┤  (Web Browser)  │    │  (Web Browser)  │
│  Port: 5000     │    │  HTTP Client    │    │  HTTP Client    │
│  192.168.1.100  │    │ 192.168.1.101   │    │ 192.168.1.102   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │
        ▼
   SQLite Database
   Logs & Backups
```

**Vorteile:**
- ✅ **Kasse:** Nur Browser erforderlich (kein Python!)
- ✅ **NAS:** Zentrale Datenhaltung, automatische Backups
- ✅ **Multi-Client:** iPad, Kasse, weitere Geräte gleichzeitig
- ✅ **Updates:** Nur auf NAS erforderlich
- ✅ **24/7 Verfügbar:** NAS läuft permanent

---

## 📋 **SCHRITT 1: NAS VORBEREITEN**

### **1.1 Ordnerstruktur auf NAS erstellen:**
```
\\[NAS-IP]\wartungsmanager\
├── app\                    # Flask Application
├── config\                 # Konfigurationsdateien
├── database\               # SQLite Database
├── logs\                   # Log Files & Backups
├── python-portable\        # Portable Python Installation
├── static\                 # CSS/JS/Images
├── templates\              # HTML Templates
├── requirements.txt        # Python Dependencies
├── run.py                 # Flask Startup Script
├── start_server.bat       # Windows Auto-Start
├── start_server.sh        # Linux Auto-Start (falls NAS Linux)
└── wartungsmanager.url    # Browser-Shortcut für Clients
```

### **1.2 Python Portable installieren (falls NAS kein Python hat):**
```bash
# Option A: Python Embedded (empfohlen)
# Download: https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-win64.zip
# Entpacken nach: \\NAS-IP\wartungsmanager\python-portable\

# Option B: Full Python Installation auf NAS
# Download: https://www.python.org/downloads/release/python-3119/
```

### **1.3 Netzwerk-Konfiguration:**
- **NAS IP:** z.B. 192.168.1.100 (statisch setzen!)
- **Port:** 5000 (oder gewünschten Port)
- **Firewall:** Port 5000 in NAS-Firewall freigeben

---

## 🚀 **SCHRITT 2: WARTUNGSMANAGER AUF NAS KOPIEREN**

### **2.1 Aktuelles Projekt kopieren:**
```bash
# Von Ihrem Entwicklungs-PC:
C:\SoftwareProjekte\WartungsManager\Source\Python\*
# Nach NAS kopieren:
\\[NAS-IP]\wartungsmanager\
```

### **2.2 Produktions-Konfiguration erstellen:**
```python
# config/production.py
import os

# Flask-Konfiguration für Produktionsumgebung
class ProductionConfig:
    # Server-Konfiguration
    HOST = '0.0.0.0'  # Alle Netzwerk-Interfaces
    PORT = 5000
    DEBUG = False
    
    # Datenbank
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database/wartungsmanager.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Sicherheit
    SECRET_KEY = 'IHR-SICHERER-SCHLUESSEL-HIER'
    
    # Logging
    LOG_FILE = 'logs/production.log'
    LOG_LEVEL = 'INFO'
    
    # Backup
    BACKUP_DIR = 'logs/backups'
    BACKUP_INTERVAL_HOURS = 6
```

---

## 📝 **SCHRITT 3: AUTO-START SCRIPTS ERSTELLEN**

### **3.1 Windows Startup Script (start_server.bat):**
```batch
@echo off
title Wartungsmanager Server - NAS
cd /d "\\[NAS-IP]\wartungsmanager"

echo ========================================
echo WARTUNGSMANAGER SERVER STARTET
echo NAS: [NAS-IP]:5000
echo ========================================

REM Python-Pfad setzen (portable oder installiert)
set PYTHON_PATH=python-portable\python.exe
if not exist "%PYTHON_PATH%" (
    set PYTHON_PATH=python
)

REM Dependencies installieren (falls erforderlich)
echo Installing dependencies...
%PYTHON_PATH% -m pip install --quiet -r requirements.txt

REM Datenbank migrieren (falls erforderlich)
echo Checking database...
%PYTHON_PATH% run_migration.py

REM Flask Server starten
echo Starting Flask server...
echo Zugänglich unter: http://[NAS-IP]:5000
echo.
echo CTRL+C zum Beenden
%PYTHON_PATH% run.py

pause
```

### **3.2 Linux Startup Script (start_server.sh):**
```bash
#!/bin/bash
cd "/volume1/wartungsmanager"  # Synology-Pfad anpassen

echo "========================================"
echo "WARTUNGSMANAGER SERVER STARTET"
echo "NAS: [NAS-IP]:5000"
echo "========================================"

# Python-Pfad prüfen
if [ -f "python-portable/bin/python3" ]; then
    PYTHON_PATH="python-portable/bin/python3"
else
    PYTHON_PATH="python3"
fi

# Dependencies installieren
echo "Installing dependencies..."
$PYTHON_PATH -m pip install --quiet -r requirements.txt

# Datenbank migrieren
echo "Checking database..."
$PYTHON_PATH run_migration.py

# Flask Server starten
echo "Starting Flask server..."
echo "Zugänglich unter: http://[NAS-IP]:5000"
$PYTHON_PATH run.py
```

---

## 💻 **SCHRITT 4: KASSEN-COMPUTER SETUP**

### **4.1 Browser-Shortcut erstellen (wartungsmanager_kasse.bat):**
```batch
@echo off
title Wartungsmanager - Kasse
echo Starte Wartungsmanager...
echo Verbinde zu NAS-Server: [NAS-IP]:5000

REM Versuche verschiedene Browser (Priorität: Chrome, Edge, Firefox)
set URL=http://[NAS-IP]:5000

if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo Starte mit Google Chrome...
    start "Wartungsmanager" "C:\Program Files\Google\Chrome\Application\chrome.exe" --new-window --kiosk %URL%
) else if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    echo Starte mit Microsoft Edge...
    start "Wartungsmanager" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --new-window --kiosk %URL%
) else (
    echo Starte mit Standard-Browser...
    start "Wartungsmanager" %URL%
)

REM Warte kurz und schließe Command-Fenster
timeout /t 3 /nobreak >nul
exit
```

### **4.2 Desktop-Shortcut erstellen (wartungsmanager.url):**
```ini
[InternetShortcut]
URL=http://[NAS-IP]:5000
IconFile=C:\Windows\System32\shell32.dll
IconIndex=14
```

### **4.3 Vollbild-Kiosk-Mode (für Kasse):**
```batch
@echo off
title Wartungsmanager Kiosk-Modus
echo Starte Wartungsmanager im Vollbild-Modus für Kassensystem...

REM Chrome im Kiosk-Modus (empfohlen für Kasse)
start "Wartungsmanager-Kiosk" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --kiosk ^
  --disable-infobars ^
  --disable-extensions ^
  --disable-dev-tools ^
  --no-first-run ^
  --fast ^
  --fast-start ^
  --disable-default-apps ^
  http://[NAS-IP]:5000

exit
```

---

## 🔧 **SCHRITT 5: AUTOMATISIERUNG & WARTUNG**

### **5.1 Auto-Start bei NAS-Boot einrichten:**

**Windows NAS (oder VM):**
```batch
REM In Windows Autostart-Ordner kopieren:
REM %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
copy "start_server.bat" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\wartungsmanager.bat"
```

**Synology NAS:**
```bash
# Startup-Script in Control Panel > Task Scheduler erstellen:
# Trigger: Boot-up
# User: root
# Command: /volume1/wartungsmanager/start_server.sh
```

**QNAP NAS:**
```bash
# Autorun.sh bearbeiten:
echo '/share/wartungsmanager/start_server.sh &' >> /etc/config/autorun.sh
```

### **5.2 Backup-Script (backup_database.bat):**
```batch
@echo off
set BACKUP_DIR=logs\backups
set DATE=%date:~10,4%-%date:~4,2%-%date:~7,2%
set TIME=%time:~0,2%-%time:~3,2%-%time:~6,2%
set TIMESTAMP=%DATE%_%TIME::=-%

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo Erstelle Backup: %TIMESTAMP%
copy "database\wartungsmanager.db" "%BACKUP_DIR%\wartungsmanager_%TIMESTAMP%.db"
copy "logs\*.log" "%BACKUP_DIR%\" 2>nul

echo Backup erstellt: %BACKUP_DIR%\wartungsmanager_%TIMESTAMP%.db
```

### **5.3 Health-Check Script (health_check.py):**
```python
#!/usr/bin/env python3
"""
Health-Check für Wartungsmanager NAS-Deployment
Prüft Server-Status und sendet Warnungen bei Problemen
"""
import requests
import sys
import os
from datetime import datetime

NAS_IP = "[NAS-IP]"
NAS_PORT = 5000
LOG_FILE = "logs/health_check.log"

def check_server():
    try:
        response = requests.get(f"http://{NAS_IP}:{NAS_PORT}/", timeout=10)
        return response.status_code == 200
    except:
        return False

def log_status(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} - {message}\n")
    print(f"{timestamp} - {message}")

if __name__ == "__main__":
    if check_server():
        log_status("✅ Server läuft normal")
        sys.exit(0)
    else:
        log_status("❌ Server nicht erreichbar!")
        sys.exit(1)
```

---

## 🌐 **SCHRITT 6: NETZWERK-ZUGRIFF TESTEN**

### **6.1 Server-Test:**
```bash
# Von NAS aus testen:
curl http://localhost:5000
# Oder Browser: http://localhost:5000

# Von anderem PC im Netzwerk:
curl http://[NAS-IP]:5000
# Oder Browser: http://[NAS-IP]:5000
```

### **6.2 Port-Test:**
```bash
# Port-Verfügbarkeit prüfen:
telnet [NAS-IP] 5000

# Oder mit PowerShell:
Test-NetConnection -ComputerName [NAS-IP] -Port 5000
```

### **6.3 Firewall-Konfiguration:**
```bash
# Windows Firewall (falls NAS Windows-basiert):
netsh advfirewall firewall add rule name="Wartungsmanager" dir=in action=allow protocol=TCP localport=5000

# Linux iptables (falls NAS Linux-basiert):
iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

---

## 📱 **SCHRITT 7: CLIENT-ZUGRIFF EINRICHTEN**

### **7.1 Alle Clients konfigurieren:**

**Kasse (Windows):**
- `wartungsmanager_kasse.bat` auf Desktop kopieren
- Doppelklick startet Browser automatisch

**iPad:**
- Safari öffnen: `http://[NAS-IP]:5000`
- "Zum Home-Bildschirm hinzufügen" für App-ähnlichen Zugriff

**Weitere PCs:**
- Browser-Bookmark: `http://[NAS-IP]:5000`
- Oder URL-Datei verwenden

### **7.2 Offline-Fallback (optional):**
```html
<!-- Für kritische Systeme: Offline-Seite erstellen -->
<!DOCTYPE html>
<html>
<head>
    <title>Wartungsmanager - Server nicht verfügbar</title>
</head>
<body>
    <h1>⚠️ Server nicht erreichbar</h1>
    <p>Der Wartungsmanager-Server auf der NAS ist nicht verfügbar.</p>
    <p>Bitte prüfen Sie:</p>
    <ul>
        <li>NAS-Stromversorgung</li>
        <li>Netzwerkverbindung</li>
        <li>Server-Status auf NAS</li>
    </ul>
    <button onclick="location.reload()">🔄 Erneut versuchen</button>
</body>
</html>
```

---

## 🎯 **DEPLOYMENT CHECKLISTE**

### **NAS-Setup:**
- [ ] Ordnerstruktur erstellt
- [ ] Python installiert/portable kopiert
- [ ] Projekt-Dateien kopiert
- [ ] Dependencies installiert
- [ ] start_server.bat/sh erstellt
- [ ] Auto-Start konfiguriert
- [ ] Firewall-Port freigegeben

### **Kassen-Setup:**
- [ ] Browser-Shortcuts erstellt
- [ ] Netzwerk-Zugriff getestet
- [ ] Kiosk-Modus konfiguriert
- [ ] Desktop-Icons erstellt

### **Test & Verifikation:**
- [ ] Server startet automatisch
- [ ] Alle Clients können zugreifen
- [ ] iPad-Touch-Bedienung funktioniert
- [ ] Backup-System funktioniert
- [ ] Health-Check läuft

---

## ⚡ **QUICK-START ZUSAMMENFASSUNG**

### **Für Sie als Setup:**
1. **NAS:** Ordner erstellen, Python kopieren, Projekt übertragen
2. **start_server.bat** anpassen (NAS-IP einsetzen) und ausführen
3. **Kasse:** `wartungsmanager_kasse.bat` erstellen und auf Desktop
4. **Test:** Browser öffnet automatisch `http://[NAS-IP]:5000`

### **Für täglichen Betrieb:**
- **NAS:** Läuft automatisch 24/7
- **Kasse:** Doppelklick auf Desktop-Icon
- **iPad:** Bookmark im Browser oder Home-Screen-App

---

**✅ Nach diesem Setup haben Sie:**
- Wartungsmanager läuft zentral auf NAS
- Kasse braucht nur Browser (kein Python!)
- iPad funktioniert popup-frei
- Automatische Backups
- 24/7 Verfügbarkeit

**Soll ich mit der Erstellung der Script-Dateien beginnen?**
