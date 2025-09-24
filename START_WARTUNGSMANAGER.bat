@echo off
title WartungsManager - Lokale Entwicklung
color 0A
echo ========================================
echo   WARTUNGSMANAGER - LOKALER START
echo ========================================
echo.

REM Zum Projektverzeichnis wechseln
cd /d "C:\SoftwareProjekte\WartungsManager\Source\Python"
if errorlevel 1 (
    echo ❌ FEHLER: Projektverzeichnis nicht gefunden!
    echo Erwarteter Pfad: C:\SoftwareProjekte\WartungsManager\Source\Python
    pause
    exit /b 1
)

echo ✅ Arbeitsverzeichnis: %CD%
echo.

REM Python-Version prüfen
echo 📋 Prüfe Python-Installation...
python --version
if errorlevel 1 (
    echo ❌ FEHLER: Python nicht gefunden!
    echo Bitte Python 3.10+ installieren
    pause
    exit /b 1
)

echo.
echo ========================================
echo   DATENBANK-PRÜFUNG
echo ========================================

REM Prüfe ob Datenbank existiert
if exist "database\wartungsmanager.db" (
    echo ✅ Datenbank gefunden: database\wartungsmanager.db
) else (
    echo ⚠️  Datenbank nicht gefunden - wird beim ersten Start erstellt
)

echo.
echo ========================================
echo   ERWEITERTE FLASCHEN-FEATURES
echo ========================================

REM Prüfe ob Migration nötig ist
echo 🔧 Überprüfe Flaschen-Rückverfolgbarkeit...
if exist "vollstaendige_flaschen_reparatur.py" (
    echo 🔄 Führe Flaschen-Reparatur aus...
    python vollstaendige_flaschen_reparatur.py
    echo.
) else (
    echo ℹ️  Reparatur-Skript nicht gefunden (normal nach abgeschlossener Migration)
)

echo.
echo ========================================
echo   SERVER START
echo ========================================

REM Backup erstellen (falls DB existiert)
if exist "database\wartungsmanager.db" (
    echo 💾 Erstelle Backup...
    set BACKUP_TIME=%date:~10,4%-%date:~4,2%-%date:~7,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%
    set BACKUP_TIME=!BACKUP_TIME: =0!
    if not exist "database\backups" mkdir "database\backups"
    copy "database\wartungsmanager.db" "database\backups\backup_!BACKUP_TIME!.db" >nul 2>&1
    echo ✅ Backup erstellt: backup_!BACKUP_TIME!.db
)

echo.
echo 🚀 Starte WartungsManager Server...
echo.
echo 📍 Lokale Adressen:
echo    • http://localhost:5000
echo    • http://127.0.0.1:5000
echo    • http://192.168.0.141:5000
echo.
echo 🌐 Netzwerk-Zugriff:
echo    • Von anderen Geräten: http://192.168.0.141:5000
echo    • iPad/Tablet: http://192.168.0.141:5000
echo.
echo 🆕 NEUE FEATURES:
echo    • Prüfungsmanagement: /pruefungsmanagement
echo    • Erweiterte Flaschen-Rückverfolgbarkeit
echo    • Automatische Flaschennummer-Generierung
echo    • Bauartzulassung und Seriennummern
echo.
echo ⏹️  CTRL+C zum Beenden
echo ========================================
echo.

REM Flask Server starten
python run.py

echo.
echo ========================================
echo   SERVER BEENDET
echo ========================================
echo WartungsManager wurde beendet.
echo.
pause
