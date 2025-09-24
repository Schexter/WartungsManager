@echo off
setlocal enabledelayedexpansion

REM Fehlerbehandlung: Bei jedem Fehler pausieren
if not "%1"=="nopause" (
    echo.
    echo WARTUNGSMANAGER INSTALLER - FEHLERGESCHÜTZTE VERSION
    echo ===================================================
    echo.
    echo Diese Datei führt den Installer aus und pausiert bei Fehlern.
    echo.
    pause
    echo.
)

REM Rufe den echten Installer auf
call "%~dp0INSTALLATION_MIT_PAUSE.bat"

REM Pausiere immer am Ende
echo.
echo Installation abgeschlossen oder Fehler aufgetreten.
pause
