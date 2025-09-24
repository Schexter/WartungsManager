@echo off
echo ====================================
echo WartungsManager - NOTFALL MIGRATION
echo ====================================
echo Direkte Migration ohne Virtual Environment
echo.

REM Ins Python-Verzeichnis wechseln
cd /d "%~dp0"
echo Aktuelles Verzeichnis: %CD%
echo.

echo Starte Notfall-Migration...
echo (Verwendet System-Python direkt)
echo.

python notfall_migration.py

if %ERRORLEVEL% equ 0 (
    echo.
    echo ✓ Notfall-Migration erfolgreich!
    echo.
    echo Jetzt Anwendung starten:
    echo python run.py
    echo.
) else (
    echo.
    echo ✗ Notfall-Migration fehlgeschlagen
    echo.
)

echo Druecken Sie eine beliebige Taste zum Beenden...
pause > nul
