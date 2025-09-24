# 🔧 WartungsManager

> **Produktionsreifes Wartungs- und Füllstandsmanagement-System**

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-proprietary-red.svg)](LICENSE)

## 📋 Übersicht

WartungsManager ist ein vollständig entwickeltes, netzwerkfähiges System zur Verwaltung von Wartungsarbeiten und Füllständen. Speziell entwickelt für den Einsatz in industriellen Umgebungen mit Touch-Interface-Unterstützung.

## ✨ Features

### Kern-Funktionalität
- 🌐 **Web-basierte Anwendung** - Zugriff von überall im Netzwerk
- 📱 **Touch-optimiert** - Speziell für iPad/Tablet-Nutzung
- 🖨️ **Druckerintegration** - 62mm Thermodrucker (ESC/POS)
- 💾 **Automatisches Backup** - NAS-Integration
- 🔧 **Kompressor-Steuerung** - Vollständige Kontrolle und Protokollierung
- 📊 **Datenbank** - SQLite mit automatischer Migration

### Technische Highlights
- Multi-Client-fähig
- Automatische Windows-Integration
- Vollautomatische Installer
- Touch-UI ohne Popups
- Echtzeit-Statusanzeigen

## 🚀 Schnellstart

### Systemanforderungen
- Windows 10/11
- Python 3.11 (wird automatisch installiert)
- 2GB RAM
- Netzwerkverbindung

### Installation

1. **Download** des Projekts
2. **Als Administrator** ausführen:
```batch
cd C:\SoftwareProjekte\WartungsManager\installer
setup_wartungsmanager_v2.bat
```

3. Nach 3-5 Minuten ist das System unter http://localhost:5000 verfügbar

### Netzwerkzugriff
- Haupt-PC: `http://localhost:5000`
- iPad/Tablet: `http://[PC-IP]:5000`
- Andere PCs: Nutze `zugriff_auf_kasse.bat`

## 🛠️ Technologie-Stack

| Komponente | Technologie |
|------------|-------------|
| Backend | Python 3.11, Flask 2.3.3 |
| Frontend | HTML5, Bootstrap 5, JavaScript |
| Datenbank | SQLite + Alembic Migrations |
| Deployment | Windows Service, Auto-Start |
| Backup | WD My Cloud NAS |

## 📁 Projektstruktur

```
WartungsManager/
├── Source/Python/       # Hauptanwendung
│   ├── app/            # Flask Application
│   ├── database/       # SQLite Datenbank
│   └── migrations/     # Alembic Migrations
├── installer/          # Installations-Scripts
├── Dokumentation/      # Projektdokumentation
├── Logs/              # Entwicklungslogs
└── Chats/             # Entwicklungs-Chats
```

## 🔌 Module

- **Füllmanager** - Verwaltung von Füllvorgängen
- **Wartungsintervalle** - Automatische Wartungsplanung
- **Patronenwechsel** - Dokumentation und Tracking
- **Kundenverwaltung** - Integrierte Kundendatenbank
- **Druckerverwaltung** - Queue-basiertes Drucksystem

## 📸 Screenshots

*[Hier könnten Screenshots eingefügt werden]*

## 🤝 Beitragen

Dieses ist ein proprietäres Projekt. Für Anfragen kontaktieren Sie bitte den Entwickler.

## 📄 Lizenz

Copyright © 2025 Hans Hahn - Alle Rechte vorbehalten

Dieses Projekt ist proprietäre Software. Keine Nutzung, Vervielfältigung oder Verteilung ohne ausdrückliche schriftliche Genehmigung.

## 📞 Support

Bei Fragen oder Problemen:
1. Konsultieren Sie die Dokumentation im `/Dokumentation` Ordner
2. Prüfen Sie die Logs unter `/Logs/error.log`
3. Nutzen Sie das Diagnose-Tool: `python_diagnose_v2.bat`

---

**Entwickelt von Hans Hahn** | Version 2.0 | Status: PRODUKTIONSREIF

Erstellt von Hans Hahn - Alle Rechte vorbehalten
