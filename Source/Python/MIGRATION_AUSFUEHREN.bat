@echo off
echo ====================================
echo WartungsManager - Datenbank Migration
echo ====================================
echo.

REM Ins Python-Verzeichnis wechseln
cd /d "%~dp0"
echo Aktuelles Verzeichnis: %CD%
echo.

REM Prüfe ob Virtual Environment existiert
if not exist "wartung_env\Scripts\activate.bat" (
    echo FEHLER: Virtual Environment nicht gefunden!
    echo Erwarteter Pfad: %CD%\wartung_env\Scripts\activate.bat
    echo.
    echo LOESUNG:
    echo 1. Virtual Environment erstellen:
    echo    python -m venv wartung_env
    echo.
    echo 2. Dependencies installieren:
    echo    wartung_env\Scripts\activate
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo Virtual Environment gefunden!
echo Aktiviere Virtual Environment...
call "wartung_env\Scripts\activate.bat"

echo.
echo Starte Datenbank-Migration...
echo.

python run_migration.py

if %ERRORLEVEL% equ 0 (
    echo.
    echo ✓ Migration erfolgreich abgeschlossen!
    echo Sie können jetzt die Anwendung starten:
    echo python run.py
    echo.
) else (
    echo.
    echo ✗ Migration fehlgeschlagen (Fehlercode: %ERRORLEVEL%)
    echo Siehe Details oben.
    echo.
)

REM Halte Fenster offen
echo Druecken Sie eine beliebige Taste zum Beenden...
pause > nul
