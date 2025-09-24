# ALTERNATIVE LÖSUNG - MANUELLE MIGRATION

## Schritt 1: Kommandozeile öffnen
- **Windows-Taste + R** → `cmd` → Enter
- **ODER:** PowerShell als Administrator öffnen

## Schritt 2: Ins Python-Verzeichnis wechseln
```cmd
cd /d "C:\SoftwareProjekte\WartungsManager\Source\Python"
```

## Schritt 3: Virtual Environment aktivieren
```cmd
wartung_env\Scripts\activate
```

**Sollte folgende Ausgabe zeigen:**
```
(wartung_env) C:\SoftwareProjekte\WartungsManager\Source\Python>
```

## Schritt 4: Migration ausführen
```cmd
python run_migration.py
```

## Schritt 5: Bei Erfolg - Anwendung starten
```cmd
python run.py
```

---

## FALLS VIRTUAL ENVIRONMENT FEHLT:

### Virtual Environment neu erstellen:
```cmd
# 1. Ins Python-Verzeichnis
cd /d "C:\SoftwareProjekte\WartungsManager\Source\Python"

# 2. Virtual Environment erstellen
python -m venv wartung_env

# 3. Aktivieren
wartung_env\Scripts\activate

# 4. Dependencies installieren
pip install -r requirements.txt

# 5. Migration ausführen
python run_migration.py
```

## Schnelltest - System prüfen:
```cmd
python run_migration.py status
```

Das sollte alle Tabellen auflisten und zeigen, welche fehlen.
