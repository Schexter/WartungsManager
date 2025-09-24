# 📡 Shelly-Integration für WartungsManager

## ❌ Problem: Shelly funktioniert nicht

Die Shelly-Integration war **nicht korrekt konfiguriert**:

1. **Hardcoded Config**: Die API hatte `enabled: False` fest einprogrammiert
2. **Zentrale Config ignoriert**: Die Flask-Config wurde nicht verwendet
3. **Keine .env-Datei**: Umgebungsvariablen fehlten

## ✅ Lösung: So aktivieren Sie Shelly

### Schritt 1: Python-Abhängigkeiten installieren
```batch
cd C:\SoftwareEntwicklung\WartungsManager-main\Source\Python
pip install python-dotenv
```

### Schritt 2: Shelly konfigurieren
```batch
python configure_shelly.py
```

Folgen Sie den Anweisungen:
- Wählen Sie "j" zum Aktivieren
- Geben Sie die IP-Adresse Ihres Shelly ein (z.B. 192.168.0.100)
- Wählen Sie Ihr Shelly-Modell (1-4)
- Optional: Username/Password falls konfiguriert

### Schritt 3: Server neu starten
```batch
python run_production.py
```

Sie sollten sehen:
```
✅ Umgebungsvariablen geladen
✅ Shelly-Integration AKTIVIERT
   IP: 192.168.0.100
   Modell: Shelly1PM
```

## 🧪 Test der Integration

### Verbindungstest:
```batch
python configure_shelly.py test
```

### Via Web-Interface:
1. Öffnen Sie http://localhost:5000
2. Navigieren Sie zu "Kompressor"
3. Der Button sollte jetzt den Shelly schalten

### Via API testen:
```batch
# Status abfragen
curl http://localhost:5000/api/shelly/kompressor/status

# Einschalten
curl -X POST http://localhost:5000/api/shelly/kompressor/einschalten

# Ausschalten
curl -X POST http://localhost:5000/api/shelly/kompressor/ausschalten
```

## 📝 Konfigurationsdatei

Die Einstellungen werden in `.env` gespeichert:
```env
SHELLY_ENABLED=true
SHELLY_IP=192.168.0.100
SHELLY_MODEL=Shelly1PM
SHELLY_USERNAME=
SHELLY_PASSWORD=
```

## 🔧 Unterstützte Shelly-Modelle

- **Shelly 1**: Einfaches Relais
- **Shelly 1PM**: Mit Leistungsmessung (EMPFOHLEN)
- **Shelly Plus 1**: Neue Generation
- **Shelly Plus 1PM**: Neue Generation mit Leistungsmessung

## 🚨 Troubleshooting

### "Shelly nicht erreichbar"
- IP-Adresse prüfen
- Shelly und PC im gleichen Netzwerk?
- Firewall-Einstellungen prüfen

### "Shelly nicht aktiviert"
- .env-Datei vorhanden?
- SHELLY_ENABLED=true gesetzt?
- Server nach Änderung neu gestartet?

### "HTTP 401 Unauthorized"
- Username/Password in Shelly-Webinterface prüfen
- Credentials in .env eintragen

## 📊 Integration in Kompressor-Modul

Die Shelly-Integration ist nahtlos in das Kompressor-Modul integriert:

1. **Kompressor Start** → Shelly Relais AN
2. **Kompressor Stop** → Shelly Relais AUS
3. **Status-Anzeige** → Leistungsaufnahme in Watt
4. **Not-Aus** → Sofortige Abschaltung

## 🎯 Nächste Schritte

Nach erfolgreicher Aktivierung:

1. **Zeitschaltungen** einrichten (geplant)
2. **Stromverbrauch** protokollieren
3. **Wartungserinnerungen** bei Überlastung
4. **Multi-Shelly** Support für mehrere Kompressoren

---

**Erstellt von Hans Hahn - Alle Rechte vorbehalten**
**Stand: 22.09.2025**
