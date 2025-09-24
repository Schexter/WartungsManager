# 🚀 SETUP-ANLEITUNG: Python 3.11 + Flask Entwicklungsumgebung

## 📋 Voraussetzungen prüfen

### 1. Python 3.11 Installation prüfen
```bash
python --version
# Sollte zeigen: Python 3.11.x

python -m pip --version
# Sollte pip Version anzeigen
```

### 2. Projekt-Verzeichnis öffnen
```bash
cd C:\SoftwareProjekte\WartungsManager\Source\Python
```

## 🔧 Entwicklungsumgebung einrichten

### 3. Virtual Environment erstellen
```bash
# Virtual Environment erstellen
python -m venv wartung_env

# Virtual Environment aktivieren (Windows)
wartung_env\Scripts\activate

# Sollte zeigen: (wartung_env) C:\SoftwareProjekte\...
```

### 4. Dependencies installieren
```bash
# Alle benötigten Pakete installieren
pip install -r requirements.txt

# Installation prüfen
pip list
```

### 5. Flask-App testen
```bash
# Flask App starten
python run.py

# Sollte zeigen:
# 🔧 WartungsManager startet...
# 📱 Touch-optimierte UI verfügbar auf: http://localhost:5000
# 🌐 Netzwerk-Zugriff: http://192.168.1.100:5000
```

## 🗄️ Datenbank initialisieren

### 6. Flask-Migrate Setup
```bash
# Migrations-Verzeichnis initialisieren
flask db init

# Erste Migration erstellen
flask db migrate -m "Initial migration"

# Migration ausführen
flask db upgrade
```

### 7. Test-Daten erstellen (optional)
```bash
# Flask Shell öffnen
flask shell

# Test-Daten erstellen
>>> from app.models.fuelling import Fuellvorgang
>>> from app import db
>>> test_vorgang = Fuellvorgang(operator="Test User")
>>> db.session.add(test_vorgang)
>>> db.session.commit()
>>> exit()
```

## 📱 Touch-UI testen

### 8. Browser-Tests
1. **Desktop-Browser:** http://localhost:5000
2. **Mobile/Tablet:** http://192.168.1.100:5000
3. **Touch-Tests:** Button-Größen, Responsive Design

### 9. Netzwerk-Zugriff testen
```bash
# IP-Adresse des Entwicklungsrechners finden
ipconfig

# Flask mit spezifischer IP starten
python run.py
# Dann von anderem Gerät: http://[IHRE_IP]:5000
```

## 🔍 Troubleshooting

### Problem: Python 3.11 nicht gefunden
**Lösung:** Python 3.11 von python.org herunterladen und installieren

### Problem: Virtual Environment Fehler
**Lösung:** 
```bash
# Neu erstellen
rmdir /s wartung_env
python -m venv wartung_env
```

### Problem: Dependencies installieren schlägt fehl
**Lösung:**
```bash
# pip upgraden
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Problem: Flask App startet nicht
**Lösung:**
```bash
# Port bereits belegt?
netstat -an | findstr :5000

# Anderen Port verwenden
set FLASK_PORT=5001
python run.py
```

### Problem: Netzwerk-Zugriff funktioniert nicht
**Lösung:**
```bash
# Windows Firewall prüfen
# Port 5000 für Python freigeben
# Router-Einstellungen prüfen (lokales Netzwerk)
```

## 📁 Datei-Struktur nach Setup

Nach erfolgreichem Setup sollte folgende Struktur vorhanden sein:

```
C:\SoftwareProjekte\WartungsManager\Source\Python\
├── wartung_env\              # Virtual Environment
├── migrations\               # Flask-Migrate Dateien
├── database\
│   └── wartungsmanager.db   # SQLite Datenbank
├── app\
│   ├── __init__.py
│   ├── models\
│   ├── routes\
│   ├── templates\
│   └── static\
├── config\
├── requirements.txt
└── run.py
```

## ✅ Setup-Checkliste

- [ ] Python 3.11 installiert und funktionsfähig
- [ ] Virtual Environment erstellt und aktiviert
- [ ] Alle Dependencies aus requirements.txt installiert
- [ ] Flask-App startet ohne Fehler auf localhost:5000
- [ ] Datenbank-Migrations funktionieren
- [ ] Netzwerk-Zugriff von anderen Geräten möglich
- [ ] Touch-UI reagiert korrekt auf Touch-Eingaben
- [ ] Base-Template lädt mit Bootstrap 5 Styling

## 🎯 Nächste Entwicklungsschritte

Nach erfolgreichem Setup:

1. **Füllvorgang-Routes implementieren** (Start/Stop Buttons)
2. **Dashboard mit Live-Timer erstellen**
3. **SQLAlchemy Models vervollständigen**
4. **Touch-optimierte Templates erweitern**
5. **API-Endpoints für AJAX-Requests**

---
**Erstellt:** 26.06.2025  
**Status:** Ready für Development  
**Support:** Bei Problemen Error-Log konsultieren oder Claude fragen
