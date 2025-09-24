@echo off
REM Füllmanager Datenbank Check und Repair
REM Erstellt von Hans Hahn - Alle Rechte vorbehalten
REM Datum: 04.07.2025

echo ================================================
echo FUELLMANAGER DATENBANK CHECK
echo ================================================
echo.

cd /d "C:\SoftwareProjekte\WartungsManager\Source\Python"

echo Pruefe Fuellmanager-Tabellen...
echo.

python check_fuellmanager_db.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ================================================
    echo FEHLER: Tabellen konnten nicht erstellt werden!
    echo ================================================
    echo.
    echo Moegliche Loesungen:
    echo 1. Starten Sie den WartungsManager neu
    echo 2. Fuehren Sie MIGRATION_AUSFUEHREN.bat aus
    echo 3. Kontaktieren Sie den Support
    echo.
) else (
    echo.
    echo ================================================
    echo ERFOLGREICH: Alle Tabellen sind bereit!
    echo ================================================
    echo.
    echo Der Fuellmanager sollte jetzt funktionieren.
    echo.
)

pause
