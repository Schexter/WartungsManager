@echo off
title Wartungsmanager Server - NAS Startup
color 0A
echo ========================================
echo   WARTUNGSMANAGER SERVER STARTUP
echo ========================================
echo.

REM NAS-IP und Port konfigurieren (ANPASSEN!)
set NAS_IP=192.168.1.100
set NAS_PORT=5000

REM Arbeitsverzeichnis auf NAS setzen
cd /d "\\%NAS_IP%\wartungsmanager"
if errorlevel 1 (
    echo ❌ FEHLER: NAS-Ordner nicht erreichbar!
    echo Prüfen Sie: \\%NAS_IP%\wartungsmanager
    pause
    exit /b 1
)

echo ✅ NAS-Verbindung OK: %CD%
echo.

REM Python-Pfad ermitteln
set PYTHON_PATH=python-portable\python.exe
if exist "%PYTHON_PATH%" (
    echo ✅ Portable Python gefunden: %PYTHON_PATH%
) else (
    set PYTHON_PATH=python
    echo ℹ️  Verwende System-Python: %PYTHON_PATH%
)

REM Python-Version prüfen
echo Prüfe Python-Version...
%PYTHON_PATH% --version
if errorlevel 1 (
    echo ❌ FEHLER: Python nicht gefunden!
    echo Bitte Python installieren oder python-portable\ Ordner erstellen
    pause
    exit /b 1
)

echo.
echo ========================================
echo   DEPENDENCIES INSTALLATION
echo ========================================

REM Pip upgrade (optional)
echo Aktualisiere pip...
%PYTHON_PATH% -m pip install --upgrade pip --quiet

REM Dependencies installieren
echo Installiere Requirements...
if exist "requirements.txt" (
    %PYTHON_PATH% -m pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo ⚠️  Warning: Einige Dependencies konnten nicht installiert werden
        echo Fortfahren trotzdem...
    ) else (
        echo ✅ Dependencies erfolgreich installiert
    )
) else (
    echo ⚠️  Warning: requirements.txt nicht gefunden
)

echo.
echo ========================================
echo   DATABASE SETUP
echo ========================================

REM Datenbank-Ordner erstellen
if not exist "database" mkdir database
echo ✅ Database-Ordner bereit

REM Log-Ordner erstellen
if not exist "logs" mkdir logs
if not exist "logs\backups" mkdir logs\backups
echo ✅ Logs-Ordner bereit

REM Datenbank-Migration (falls erforderlich)
if exist "run_migration.py" (
    echo Führe Datenbank-Migration aus...
    %PYTHON_PATH% run_migration.py
) else if exist "migrations" (
    echo Führe Alembic-Migration aus...
    %PYTHON_PATH% -m alembic upgrade head
)

echo.
echo ========================================
echo   SERVER STARTUP
echo ========================================

REM Backup vor Start (optional)
if exist "database\wartungsmanager.db" (
    echo Erstelle Backup vor Start...
    set BACKUP_TIMESTAMP=%date:~10,4%-%date:~4,2%-%date:~7,2%_%time:~0,2%-%time:~3,2%
    copy "database\wartungsmanager.db" "logs\backups\startup_backup_%BACKUP_TIMESTAMP::=-%.db" >nul 2>&1
    echo ✅ Backup erstellt
)

REM Server-Konfiguration
echo.
echo 🌐 Server wird gestartet...
echo 📍 Adresse: http://%NAS_IP%:%NAS_PORT%
echo 📁 Arbeitsverzeichnis: %CD%
echo 💾 Datenbank: database\wartungsmanager.db
echo 📝 Logs: logs\
echo.
echo ========================================
echo   ZUGRIFF VON CLIENTS:
echo ========================================
echo 💻 Kasse: Doppelklick auf wartungsmanager_kasse.bat
echo 📱 iPad: Browser → http://%NAS_IP%:%NAS_PORT%
echo 🌐 Alle Browser: http://%NAS_IP%:%NAS_PORT%
echo.
echo ⏹️  CTRL+C zum Beenden des Servers
echo ========================================
echo.

REM Flask Server starten
%PYTHON_PATH% run.py

echo.
echo ========================================
echo   SERVER BEENDET
echo ========================================
echo Der Wartungsmanager-Server wurde beendet.
echo.
pause
