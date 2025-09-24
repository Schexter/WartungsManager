# DATABASE INITIALIZATION - WartungsManager

## 🗄️ **DATENBANK-SETUP BEFEHLE**

### **Schritt 1: Flask App stoppen**
```powershell
# Im Terminal wo Flask läuft: Ctrl+C drücken
```

### **Schritt 2: Flask-Migrate initialisieren**
```powershell
# Erstellt migrations/ Verzeichnis
flask db init
```

### **Schritt 3: Erste Migration erstellen**
```powershell
# Analysiert Models und erstellt Migration
flask db migrate -m "Initial database schema"
```

### **Schritt 4: Migration ausführen**
```powershell
# Erstellt SQLite Datenbank und alle Tabellen
flask db upgrade
```

### **Schritt 5: App neu starten**
```powershell
python run.py
```

## 📋 **WAS PASSIERT:**

### **Nach `flask db init`:**
```
migrations/
├── alembic.ini
├── env.py
├── README
├── script.py.mako
└── versions/
```

### **Nach `flask db migrate`:**
```
migrations/versions/
└── 001_initial_database_schema.py  # Migration-Script
```

### **Nach `flask db upgrade`:**
```
database/
└── wartungsmanager.db  # SQLite Datenbank mit allen Tabellen
```

## ✅ **TABELLEN DIE ERSTELLT WERDEN:**

1. **fuellvorgaenge** - Füllvorgänge mit Start/Stop-Zeiten
2. **wartungen** - Wartungsintervalle und -durchführungen  
3. **handbefuellungen** - Molekular-/Kohlefilter-Protokolle
4. **users** - Benutzer-Management
5. **alembic_version** - Migration-Tracking

## 🚀 **NACH ERFOLGREICHER INITIALISIERUNG:**

Die App startet ohne Fehler und zeigt:
```
🔧 WartungsManager startet...
📱 Touch-optimierte UI verfügbar auf: http://localhost:5000
🌐 Netzwerk-Zugriff: http://192.168.0.50:5000
📱 Von allen Netzwerk-Geräten: http://[PC-IP]:5000
🐍 Python Version: 3.10.11
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

## 💡 **TROUBLESHOOTING:**

### **Problem: `flask` command not found**
```powershell
# Flask CLI über Python aufrufen
python -m flask db init
python -m flask db migrate -m "Initial schema" 
python -m flask db upgrade
```

### **Problem: Migration Fehler**
```powershell
# Migration-Verzeichnis löschen und neu starten
rmdir /s migrations
flask db init
flask db migrate -m "Fresh start"
flask db upgrade
```

---
**Status:** Bereit für Datenbank-Initialisierung  
**Dauer:** 2-3 Minuten  
**Result:** Vollständig funktionale SQLite Datenbank
