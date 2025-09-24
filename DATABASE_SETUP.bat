@echo off
title WartungsManager - DATENBANK SETUP
color 0A
echo =========================================================
echo   WARTUNGSMANAGER - DATENBANK SETUP
echo =========================================================
echo   Erstellt fehlende SQLite-Datenbank
echo   Erstellt von Hans Hahn - Alle Rechte vorbehalten
echo =========================================================
echo.

cd /d "C:\SoftwareEntwicklung\WartungsManager-main\Source\Python"

echo 📁 Arbeitsverzeichnis: %CD%
echo.

REM Datenbank-Verzeichnis erstellen
if not exist "..\..\database" mkdir "..\..\database"
echo ✅ Database-Verzeichnis erstellt: ..\..\database
echo.

REM Python-Script für Datenbank-Initialisierung erstellen
echo 🔧 Erstelle Datenbank-Initialisierung...
(
echo from app import create_app, db
echo.
echo print^("🔧 Datenbank-Initialisierung startet..."^)
echo.
echo # App erstellen
echo app = create_app^(^)
echo.
echo with app.app_context^(^):
echo     try:
echo         # Alle Tabellen erstellen
echo         db.create_all^(^)
echo         print^("✅ Alle Tabellen erfolgreich erstellt!"^)
echo         
echo         # Test-Verbindung
echo         result = db.engine.execute^(db.text^("SELECT 1"^)^)
echo         print^("✅ Datenbank-Verbindung erfolgreich getestet!"^)
echo         
echo         print^("🎉 Datenbank-Setup abgeschlossen!"^)
echo         
echo     except Exception as e:
echo         print^(f"❌ FEHLER beim Datenbank-Setup: {e}"^)
echo         print^("💡 Tipp: Prüfen Sie Dateiberechtigungen im database-Ordner"^)
) > init_database.py

echo ✅ Initialisierungsskript erstellt!
echo.

echo 🚀 Führe Datenbank-Initialisierung aus...
python init_database.py

echo.
echo =========================================================
echo   DATENBANK SETUP ABGESCHLOSSEN!
echo =========================================================
echo.
echo ✅ SQLite-Datenbank wurde erstellt!
echo 📁 Speicherort: database\wartungsmanager.db
echo.
echo 🚀 WARTUNGSMANAGER JETZT STARTEN:
echo    cd ..\..
echo    python run_production_REPARIERT.py
echo.
echo 🌐 Web-UI: http://localhost:5000
echo.
pause
