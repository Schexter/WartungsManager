@echo off
title Wartungsmanager - Automatisches Backup System
color 0E

REM Backup-Konfiguration
set BACKUP_DIR=logs\backups
set SOURCE_DB=database\wartungsmanager.db
set SOURCE_LOGS=logs\*.log

REM Zeitstempel erstellen
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do set DATE=%%c-%%a-%%b
for /f "tokens=1-3 delims=: " %%a in ('time /t') do set TIME=%%a-%%b-%%c
set TIMESTAMP=%DATE%_%TIME: =0%
set TIMESTAMP=%TIMESTAMP::=-%

echo ========================================
echo   WARTUNGSMANAGER BACKUP SYSTEM
echo ========================================
echo.
echo 💾 Erstelle Backup: %TIMESTAMP%
echo 📁 Backup-Verzeichnis: %BACKUP_DIR%
echo 🗄️  Quelle Database: %SOURCE_DB%
echo 📝 Quelle Logs: %SOURCE_LOGS%
echo.

REM Backup-Verzeichnis erstellen falls nicht vorhanden
if not exist "%BACKUP_DIR%" (
    echo 📁 Erstelle Backup-Verzeichnis...
    mkdir "%BACKUP_DIR%"
    echo ✅ Verzeichnis erstellt: %BACKUP_DIR%
)

REM Datenbank-Backup
if exist "%SOURCE_DB%" (
    echo 💾 Sichere Datenbank...
    copy "%SOURCE_DB%" "%BACKUP_DIR%\wartungsmanager_%TIMESTAMP%.db" >nul
    if exist "%BACKUP_DIR%\wartungsmanager_%TIMESTAMP%.db" (
        echo ✅ Datenbank-Backup erstellt
        
        REM Dateigröße anzeigen
        for %%I in ("%BACKUP_DIR%\wartungsmanager_%TIMESTAMP%.db") do (
            echo    📊 Größe: %%~zI Bytes
        )
    ) else (
        echo ❌ FEHLER: Datenbank-Backup fehlgeschlagen!
    )
) else (
    echo ⚠️  WARNING: Datenbank nicht gefunden: %SOURCE_DB%
)

REM Log-Backup
echo.
echo 📝 Sichere Log-Dateien...
set LOG_BACKUP_COUNT=0
for %%f in (%SOURCE_LOGS%) do (
    if exist "%%f" (
        copy "%%f" "%BACKUP_DIR%\%%~nf_%TIMESTAMP%.log" >nul
        set /a LOG_BACKUP_COUNT+=1
    )
)
echo ✅ %LOG_BACKUP_COUNT% Log-Dateien gesichert

REM Konfiguration-Backup (optional)
if exist "config\production.py" (
    echo 🔧 Sichere Konfiguration...
    copy "config\production.py" "%BACKUP_DIR%\production_%TIMESTAMP%.py" >nul
    echo ✅ Konfiguration gesichert
)

echo.
echo ========================================
echo   BACKUP-BEREINIGUNG
echo ========================================

REM Alte Backups löschen (älter als 30 Tage)
echo 🧹 Lösche alte Backups (älter als 30 Tage)...
forfiles /p "%BACKUP_DIR%" /s /m *.db /d -30 /c "cmd /c del @path" 2>nul
forfiles /p "%BACKUP_DIR%" /s /m *.log /d -30 /c "cmd /c del @path" 2>nul
forfiles /p "%BACKUP_DIR%" /s /m *.py /d -30 /c "cmd /c del @path" 2>nul

REM Anzahl verbleibender Backups zählen
set BACKUP_COUNT=0
for %%f in ("%BACKUP_DIR%\*.db") do set /a BACKUP_COUNT+=1

echo ✅ Bereinigung abgeschlossen
echo 📊 Verbleibende Backups: %BACKUP_COUNT%

echo.
echo ========================================
echo   BACKUP ABGESCHLOSSEN
echo ========================================
echo.
echo ✅ Backup erfolgreich erstellt!
echo 📁 Speicherort: %BACKUP_DIR%
echo 🕐 Zeitstempel: %TIMESTAMP%
echo.
echo 💡 Tipp: Starten Sie dieses Script regelmäßig
echo    oder fügen Sie es zu Windows Task Scheduler hinzu
echo.

REM Backup-Zusammenfassung in Log schreiben
echo %date% %time% - Backup erstellt: %TIMESTAMP% >> logs\backup.log

REM Optionale Pause (für manuellen Start)
if "%1"=="auto" (
    echo ℹ️  Automatisches Backup - Fenster schließt in 3 Sekunden
    timeout /t 3 /nobreak >nul
) else (
    echo ℹ️  Drücken Sie eine Taste um fortzufahren...
    pause >nul
)
