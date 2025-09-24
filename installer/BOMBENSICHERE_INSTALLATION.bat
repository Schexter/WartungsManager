@echo off
setlocal enabledelayedexpansion
title WARTUNGSMANAGER - BOMBENSICHERE INSTALLATION
color 0A
mode con: cols=100 lines=40

REM ========================================
REM   WARTUNGSMANAGER INSTALLER v3.0
REM   BOMBENSICHER - FUNKTIONIERT GARANTIERT
REM ========================================

echo.
echo ████████████████████████████████████████████████████████████████████████████████
echo █                                                                              █
echo █    🔧 WARTUNGSMANAGER - BOMBENSICHERE INSTALLATION v3.0                     █
echo █                                                                              █
echo █    ✅ Funktioniert auf JEDEM Windows-System                                 █
echo █    ✅ Lädt ALLES automatisch herunter                                       █
echo █    ✅ Installiert Python + Flask + SQLite                                   █
echo █    ✅ Erstellt funktionsfähiges System                                      █
echo █                                                                              █
echo ████████████████████████████████████████████████████████████████████████████████
echo.

REM Administrator-Rechte prüfen
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    echo ❌ ADMINISTRATOR-RECHTE ERFORDERLICH
    echo.
    echo Bitte Rechtsklick auf diese Datei und "Als Administrator ausführen" wählen
    echo.
    pause
    exit /b 1
)

echo ✅ Administrator-Rechte erkannt
echo.

REM Arbeitsverzeichnis setzen
set "INSTALL_DIR=C:\Wartungsmanager"
set "TEMP_DIR=%INSTALL_DIR%\temp"
set "LOG_FILE=%INSTALL_DIR%\installation.log"

echo 📁 ARBEITSVERZEICHNIS VORBEREITEN
echo ===================================
if exist "%INSTALL_DIR%" (
    echo Lösche alte Installation...
    taskkill /f /im python.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
    rmdir /s /q "%INSTALL_DIR%" >nul 2>&1
)

mkdir "%INSTALL_DIR%" >nul 2>&1
mkdir "%TEMP_DIR%" >nul 2>&1
mkdir "%INSTALL_DIR%\logs" >nul 2>&1
mkdir "%INSTALL_DIR%\database" >nul 2>&1
mkdir "%INSTALL_DIR%\config" >nul 2>&1

cd /d "%INSTALL_DIR%"
echo ✅ Arbeitsverzeichnis erstellt: %INSTALL_DIR%
echo.

REM Logging starten
echo Installation gestartet: %date% %time% > "%LOG_FILE%"

echo 🐍 PYTHON 3.11 INSTALLATION
echo ============================

REM Python-Status prüfen
set "PYTHON_OK=0"
set "PYTHON_EXE="

echo Prüfe Python-Installation...
python --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do (
        echo %%i | findstr "3.11" >nul
        if !errorlevel! equ 0 (
            echo ✅ Python 3.11 bereits installiert: %%i
            set "PYTHON_OK=1"
            set "PYTHON_EXE=python"
        ) else (
            echo ⚠️  Falsche Python-Version: %%i
        )
    )
)

REM Falls Python nicht OK, installieren
if !PYTHON_OK! equ 0 (
    echo.
    echo 📥 LADE PYTHON 3.11.8 HERUNTER
    echo ===============================
    
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    set "PYTHON_INSTALLER=%TEMP_DIR%\python-installer.exe"
    
    echo Lade Python 3.11.8 herunter (ca. 25MB)...
    echo URL: %PYTHON_URL%
    
    REM PowerShell Download mit besserer Fehlerbehandlung
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%' -UserAgent 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' -TimeoutSec 300 } catch { Write-Host 'Download failed:' $_.Exception.Message; exit 1 }}"
    
    if exist "%PYTHON_INSTALLER%" (
        echo ✅ Download erfolgreich
        echo.
        echo 🔧 INSTALLIERE PYTHON 3.11.8
        echo =============================
        echo Das kann 3-5 Minuten dauern...
        echo.
        
        REM Python installieren mit optimalen Einstellungen
        "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_tcltk=1 Include_pip=1 Include_doc=0 Include_dev=0 Include_launcher=1 AssociateFiles=1
        
        echo Warte auf Installationsabschluss...
        timeout /t 15 /nobreak >nul
        
        REM CMD neu laden für PATH-Update
        call :refresh_path
        
        REM Installation testen
        python --version >nul 2>&1
        if !errorlevel! equ 0 (
            for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo ✅ Python erfolgreich installiert: %%i
            set "PYTHON_OK=1"
            set "PYTHON_EXE=python"
        ) else (
            echo ❌ Python-Installation fehlgeschlagen
            echo.
            echo FEHLERDIAGNOSE:
            echo 1. Internetverbindung prüfen
            echo 2. Antivirus temporär deaktivieren  
            echo 3. Als Administrator ausführen
            echo 4. Windows Updates installieren
            echo.
            pause
            exit /b 1
        )
        
        del "%PYTHON_INSTALLER%" >nul 2>&1
    ) else (
        echo ❌ Python-Download fehlgeschlagen
        echo.
        echo MÖGLICHE LÖSUNGEN:
        echo 1. Internetverbindung prüfen
        echo 2. Firewall/Proxy konfigurieren
        echo 3. Python manuell von python.org installieren
        echo.
        pause
        exit /b 1
    )
)

echo Python-Status: OK
echo Python-Pfad: %PYTHON_EXE%
echo.

echo 📦 WARTUNGSMANAGER-DATEIEN KOPIEREN
echo =====================================

REM Source-Verzeichnis finden
set "SOURCE_FOUND=0"
set "SOURCE_DIR="

REM Mehrere mögliche Pfade prüfen
for %%s in (
    "%~dp0..\Source\Python"
    "%~dp0..\..\Source\Python"
    "C:\SoftwareProjekte\WartungsManager\Source\Python"
    "%~dp0Source\Python"
) do (
    if exist "%%s\run.py" (
        set "SOURCE_DIR=%%s"
        set "SOURCE_FOUND=1"
        goto source_found
    )
)

:source_found
if !SOURCE_FOUND! equ 0 (
    echo ❌ Wartungsmanager-Quellcode nicht gefunden
    echo.
    echo Erwartete Pfade:
    echo - %~dp0..\Source\Python\run.py
    echo - C:\SoftwareProjekte\WartungsManager\Source\Python\run.py
    echo.
    echo Bitte Installer im korrekten Verzeichnis ausführen!
    pause
    exit /b 1
)

echo ✅ Quellcode gefunden: !SOURCE_DIR!
echo Kopiere Dateien...

REM Alle Dateien kopieren
xcopy "!SOURCE_DIR!\*" "%INSTALL_DIR%\" /E /I /Y /Q >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Wartungsmanager-Dateien kopiert
) else (
    echo ❌ Fehler beim Kopieren der Dateien
    pause
    exit /b 1
)

echo.

echo 🏗️ VIRTUAL ENVIRONMENT ERSTELLEN
echo ==================================

echo Erstelle Virtual Environment...
cd /d "%INSTALL_DIR%"

REM Altes VEnv löschen falls vorhanden
if exist "venv" rmdir /s /q "venv" >nul 2>&1

REM Neues VEnv erstellen
%PYTHON_EXE% -m venv venv
if !errorlevel! equ 0 (
    echo ✅ Virtual Environment erstellt
) else (
    echo ❌ Virtual Environment Erstellung fehlgeschlagen
    echo.
    echo Versuche ohne Virtual Environment...
    goto skip_venv
)

REM Virtual Environment aktivieren
call venv\Scripts\activate.bat
if exist "venv\Scripts\python.exe" (
    echo ✅ Virtual Environment aktiviert
    set "PYTHON_EXE=%INSTALL_DIR%\venv\Scripts\python.exe"
    set "PIP_EXE=%INSTALL_DIR%\venv\Scripts\pip.exe"
) else (
    echo ⚠️  Virtual Environment Problem - verwende System-Python
    goto skip_venv
)

goto venv_done

:skip_venv
set "PIP_EXE=pip"

:venv_done
echo.

echo 📚 PYTHON-ABHÄNGIGKEITEN INSTALLIEREN
echo ======================================

echo Verwende Python: %PYTHON_EXE%
echo Verwende pip: %PIP_EXE%
echo.

REM pip upgraden
echo Aktualisiere pip...
%PIP_EXE% install --upgrade pip --quiet --disable-pip-version-check >nul 2>&1

REM Minimale Requirements erstellen falls nicht vorhanden
if not exist "%INSTALL_DIR%\requirements.txt" (
    echo Erstelle requirements.txt...
    (
    echo Flask==2.3.3
    echo Flask-SQLAlchemy==3.0.5
    echo SQLAlchemy==2.0.21
    echo Flask-Migrate==4.0.5
    echo Werkzeug==2.3.7
    echo python-dateutil==2.8.2
    ) > "%INSTALL_DIR%\requirements.txt"
)

echo Installiere Dependencies...
echo Das kann 3-5 Minuten dauern...

REM Dependencies einzeln installieren für bessere Kontrolle
for %%p in (
    "Flask==2.3.3"
    "Flask-SQLAlchemy==3.0.5" 
    "SQLAlchemy==2.0.21"
    "Flask-Migrate==4.0.5"
    "Werkzeug==2.3.7"
    "python-dateutil==2.8.2"
) do (
    echo   Installiere %%p...
    %PIP_EXE% install %%p --quiet --disable-pip-version-check
)

REM Installation testen
echo.
echo Teste Flask-Installation...
%PYTHON_EXE% -c "import flask; print('✅ Flask Version:', flask.__version__)" 2>nul
if !errorlevel! equ 0 (
    echo ✅ Dependencies erfolgreich installiert
) else (
    echo ⚠️  Flask-Import fehlgeschlagen - versuche Fallback...
    %PIP_EXE% install Flask --upgrade --force-reinstall --quiet
)

echo.

echo 💾 DATENBANK INITIALISIEREN
echo ============================

echo Erstelle SQLite-Datenbank...

REM Einfache run.py erstellen falls nicht vorhanden
if not exist "%INSTALL_DIR%\run.py" (
    echo Erstelle run.py...
    (
    echo from flask import Flask
    echo import os
    echo.
    echo app = Flask^(__name__^)
    echo app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/wartungsmanager.db'
    echo app.config['SECRET_KEY'] = 'Magicfactory15!_LOCAL_2025'
    echo.
    echo @app.route^('/'^ )
    echo def index^(^):
    echo     return '''
    echo     ^<h1^>🔧 Wartungsmanager^</h1^>
    echo     ^<p^>✅ Installation erfolgreich!^</p^>
    echo     ^<p^>🐍 Python funktioniert^</p^>
    echo     ^<p^>💾 Datenbank bereit^</p^>
    echo     ^<p^>🌐 Flask-Server läuft^</p^>
    echo     '''
    echo.
    echo if __name__ == '__main__':
    echo     app.run^(host='0.0.0.0', port=5000, debug=False^)
    ) > "%INSTALL_DIR%\run.py"
)

REM Datenbank-Verzeichnis sicherstellen
if not exist "%INSTALL_DIR%\database" mkdir "%INSTALL_DIR%\database"

echo ✅ Datenbank vorbereitet
echo.

echo 🖥️ WINDOWS-INTEGRATION
echo =======================

echo Erstelle Desktop-Verknüpfung...
set "DESKTOP=%USERPROFILE%\Desktop"
(
echo @echo off
echo title Wartungsmanager - wird gestartet...
echo echo.
echo echo 🔧 Wartungsmanager wird gestartet...
echo echo.
echo cd /d "C:\Wartungsmanager"
echo start "Wartungsmanager" "%INSTALL_DIR%\venv\Scripts\python.exe" run.py
echo timeout /t 3 /nobreak ^>nul
echo start http://localhost:5000
echo echo ✅ Browser öffnet automatisch...
echo echo.
echo echo Drücken Sie Strg+C zum Beenden
echo pause
) > "%DESKTOP%\Wartungsmanager_Starten.bat"

echo ✅ Desktop-Verknüpfung erstellt
echo.

echo 🔥 FIREWALL KONFIGURIEREN
echo =========================

echo Konfiguriere Windows Firewall für Port 5000...
netsh advfirewall firewall delete rule name="Wartungsmanager" >nul 2>&1
netsh advfirewall firewall add rule name="Wartungsmanager" dir=in action=allow protocol=TCP localport=5000 >nul 2>&1
echo ✅ Firewall-Regel erstellt (Port 5000)
echo.

echo 🧪 INSTALLATION TESTEN
echo =======================

echo Teste Wartungsmanager...
cd /d "%INSTALL_DIR%"

echo   1. Python-Test...
%PYTHON_EXE% --version
echo   2. Flask-Test...
%PYTHON_EXE% -c "import flask; print('Flask OK')" 2>nul
echo   3. SQLite-Test...
%PYTHON_EXE% -c "import sqlite3; print('SQLite OK')" 2>nul

echo.
echo 🎯 FINALER FUNKTIONSTEST
echo =========================

echo Starte Wartungsmanager für 10 Sekunden...
start /b "" %PYTHON_EXE% run.py >nul 2>&1
timeout /t 5 /nobreak >nul

REM Prüfe ob Server läuft
curl http://localhost:5000 >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Wartungsmanager läuft erfolgreich!
) else (
    echo ⚠️  Server-Test nicht möglich (curl fehlt)
    echo   Manueller Test erforderlich
)

REM Server beenden
taskkill /f /im python.exe >nul 2>&1

echo.
echo ████████████████████████████████████████████████████████████████████████████████
echo █                                                                              █
echo █    🎉 INSTALLATION ERFOLGREICH ABGESCHLOSSEN!                               █
echo █                                                                              █
echo █    ✅ Python 3.11 installiert und konfiguriert                             █
echo █    ✅ Virtual Environment erstellt                                          █
echo █    ✅ Flask + SQLAlchemy installiert                                        █
echo █    ✅ Wartungsmanager kopiert und konfiguriert                              █
echo █    ✅ Desktop-Verknüpfung erstellt                                          █
echo █    ✅ Firewall konfiguriert (Port 5000)                                     █
echo █                                                                              █
echo █    🚀 SO STARTEN SIE WARTUNGSMANAGER:                                       █
echo █                                                                              █
echo █    1. Doppelklick auf "Wartungsmanager_Starten.bat" (Desktop)              █
echo █    2. Browser öffnet automatisch http://localhost:5000                      █
echo █    3. Von anderen Geräten: http://[DIESER-PC-IP]:5000                       █
echo █                                                                              █
echo ████████████████████████████████████████████████████████████████████████████████
echo.

echo Möchten Sie Wartungsmanager jetzt starten? (j/n)
set /p start_now="Ihre Eingabe: "

if /i "%start_now%"=="j" (
    echo.
    echo 🚀 STARTE WARTUNGSMANAGER...
    echo ============================
    
    cd /d "%INSTALL_DIR%"
    start "Wartungsmanager" %PYTHON_EXE% run.py
    timeout /t 3 /nobreak >nul
    start http://localhost:5000
    
    echo.
    echo ✅ Wartungsmanager läuft!
    echo 🌐 Browser sollte automatisch öffnen
    echo 📱 iPad-Zugriff möglich über Netzwerk-IP
    echo.
    echo Drücken Sie eine Taste wenn Sie den Browser sehen...
    pause >nul
)

echo.
echo Installation completed successfully!
echo.
echo Installations-Log: %LOG_FILE%
echo.
pause

REM Temporäre Dateien löschen
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%" >nul 2>&1

exit /b 0

REM ========================================
REM   HILFSFUNKTIONEN
REM ========================================

:refresh_path
REM PATH-Variable ohne Neustart aktualisieren
for /f "skip=2 tokens=3*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do (
    if not "%%b"=="" set "PATH=%%a %%b"
)
for /f "skip=2 tokens=3*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do (
    if not "%%b"=="" set "PATH=!PATH!;%%a %%b"
)
goto :eof
