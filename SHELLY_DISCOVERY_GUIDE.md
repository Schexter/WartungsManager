# 🔍 Shelly Auto-Discovery & Smart Home Integration

## ✨ Das NEUE Feature: Automatische Shelly-Erkennung

Wie bei **Home Assistant** - nur einfacher! Der WartungsManager findet automatisch ALLE Shelly-Geräte in Ihrem Netzwerk und lässt Sie diese als Widgets einrichten.

## 🚀 So funktioniert's

### 1️⃣ Shelly-Discovery starten
```batch
cd C:\SoftwareEntwicklung\WartungsManager-main\Source\Python
python shelly_discovery.py
```

### 2️⃣ Was passiert dann?

Das System:
1. **Scannt Ihr Netzwerk** (192.168.0.1 - 192.168.0.254)
2. **Findet alle Shellys** automatisch
3. **Zeigt Details** zu jedem Gerät:
   - Modell (Shelly 1, Shelly 1PM, Plus, etc.)
   - IP-Adresse
   - MAC-Adresse
   - Leistungsmessung verfügbar?
   - Anzahl Relais

### 3️⃣ Kompressor-Shelly zuweisen

Sie werden gefragt:
```
Welches Gerät soll den KOMPRESSOR steuern?
```

Wählen Sie die Nummer des Shellys, der Ihren Kompressor schaltet.
Geben Sie einen Namen ein, z.B. "K14 Hauptkompressor"

### 4️⃣ Dashboard-Widgets hinzufügen

Für jedes weitere gefundene Shelly:
```
Als Widget hinzufügen? (j/n)
```

Bei "j" können Sie einen Namen vergeben:
- "Werkstatt-Licht"
- "Flaschenlager"
- "Außenbeleuchtung"
- etc.

## 📊 Das neue Dashboard

Nach dem Setup erreichen Sie das Dashboard unter:
```
http://localhost:5000/shelly/dashboard
```

### Features:

**Kompressor-Steuerung** (großes Widget)
- 🔴/🟢 Status-Anzeige
- ⚡ Leistungsanzeige in Watt
- 🔘 Ein/Aus-Schalter
- Direkt verknüpft mit Kompressor-Modul

**Weitere Geräte** (kleine Widgets)
- Individuelle Schalter für jedes Gerät
- Live-Status-Updates
- Leistungsmessung (wenn verfügbar)
- Touch-optimiert für iPad

## 🔧 Kommandos

```batch
# Erstes Setup / Neu-Scan
python shelly_discovery.py

# Geräte-Liste anzeigen
python shelly_discovery.py list

# Alle Geräte testen
python shelly_discovery.py test

# Netzwerk neu scannen
python shelly_discovery.py scan
```

## 🎮 Integration in WartungsManager

### Kompressor-Modul
Wenn Sie im Hauptmenü auf "Kompressor Start" klicken:
1. Wird das zugewiesene Shelly-Gerät eingeschaltet
2. Betriebsstunden werden gezählt
3. Leistungsaufnahme wird angezeigt

### Dashboard-Widgets
- Alle als Widget konfigurierten Shellys erscheinen automatisch
- Live-Updates alle 5 Sekunden
- Touch-optimierte Schalter
- Responsive Design für alle Geräte

## 📝 Konfigurationsdatei

Die Einstellungen werden gespeichert in:
```
C:\SoftwareEntwicklung\WartungsManager-main\Source\Python\shelly_devices.json
```

Beispiel:
```json
[
  {
    "ip": "192.168.0.100",
    "mac": "A4CF12345678",
    "name": "shelly1pm-12345",
    "model": "Shelly1PM",
    "gen": 1,
    "role": "kompressor",
    "custom_name": "K14 Hauptkompressor",
    "has_power_meter": true
  },
  {
    "ip": "192.168.0.101",
    "model": "ShellyPlus1",
    "gen": 2,
    "role": "widget",
    "custom_name": "Werkstatt-Licht"
  }
]
```

## 🚨 Troubleshooting

### "Keine Shellys gefunden"
- ✅ Shellys und PC im gleichen Netzwerk?
- ✅ Windows-Firewall deaktiviert?
- ✅ Richtiges Subnetz? (Standard: 192.168.0.x)
- ✅ Shellys haben feste IP-Adressen?

### "Shelly nicht erreichbar"
- ✅ IP-Adresse noch gültig?
- ✅ Shelly hat Strom?
- ✅ WLAN-Verbindung ok?

### "Schalter reagiert nicht"
- ✅ Shelly-Firmware aktuell?
- ✅ Keine Passwort-Sperre aktiv?
- ✅ Cloud-Modus deaktiviert?

## 🎯 Vorteile gegenüber einfacher Integration

| Alte Version | NEUE Auto-Discovery |
|-------------|-------------------|
| Eine IP manuell | Findet ALLE automatisch |
| Nur Kompressor | Unbegrenzte Widgets |
| Keine Übersicht | Live-Dashboard |
| Config-Datei editieren | Interaktives Setup |
| Kein Status | Live-Leistungsanzeige |

## 🚀 Nächste geplante Features

- **Szenen**: Mehrere Shellys gleichzeitig schalten
- **Zeitschaltungen**: Automatisches Ein/Aus
- **Energiestatistik**: Verbrauch protokollieren
- **Alarme**: Bei Überlast oder Ausfall
- **Mobile App**: Steuerung von unterwegs

## 💡 Pro-Tipps

1. **Feste IPs vergeben**: In der FritzBox den Shellys feste IPs zuweisen
2. **Namen vergeben**: Aussagekräftige Namen für einfache Zuordnung
3. **Backup**: `shelly_devices.json` regelmäßig sichern
4. **Updates**: Shelly-Firmware aktuell halten

---

**Das ist Smart-Home-Integration auf Enterprise-Level!** 🎉

Viel besser als die ursprüngliche simple Lösung - jetzt haben Sie ein vollwertiges Shelly-Control-Center integriert in den WartungsManager.

---

**Erstellt von Hans Hahn - Alle Rechte vorbehalten**
**Version: 2.1 - Smart Home Edition**
**Stand: 22.09.2025**
