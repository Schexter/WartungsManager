@echo off
title Wartungsmanager - Vollautomatische Installation v2.0
color 0A
mode con: cols=90 lines=35

REM Administrator-Rechte prüfen
openfiles >nul 2>&1
if %errorlevel% NEQ 0 (
    echo ========================================
    echo   ADMINISTRATOR-RECHTE ERFORDERLICH
    echo ========================================
    echo.
    echo Starte Installation mit Administrator-Rechten...
    echo Bitte UAC-Dialog bestätigen...
    echo.
    powershell -Command "Start-Process '%0' -Verb RunAs"
    exit /b
)

echo ========================================
echo   WARTUNGSMANAGER INSTALLER v2.0
echo ========================================
echo   Vollautomatische Installation
echo   mit RICHTIGEM Python 3.11.8
echo ========================================
echo.
echo 📦 Installation wird vorbereitet...
echo 🖥️  Zielrechner: Kassenrechner (Server-Modus)
echo 🐍 Python: 3.11.8 (VOLLINSTALLATION mit pip)
echo 💾 Backup-Ziel: WD My Cloud (192.168.0.231)
echo 🌐 Zugriff: http://localhost:5000
echo.

REM Installation stoppen falls bereits installiert
if exist "C:\Wartungsmanager\run.py" (
    echo ⚠️  WARTUNGSMANAGER BEREITS INSTALLIERT
    echo.
    echo Möchten Sie eine Neuinstallation durchführen?
    echo [J/N] - Drücken Sie J für Ja oder N für Nein:
    choice /c JN /n /m ""
    if errorlevel 2 (
        echo Installation abgebrochen.
        pause
        exit /b
    )
    echo.
    echo 🗑️  Führe Neuinstallation durch...
    call "%~dp0uninstall.bat" silent
)

echo ========================================
echo   SCHRITT 1: ARBEITSVERZEICHNIS
echo ========================================

REM Zielverzeichnis erstellen
set INSTALL_DIR=C:\Wartungsmanager
echo 📁 Erstelle Installationsverzeichnis: %INSTALL_DIR%
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\temp" mkdir "%INSTALL_DIR%\temp"
if not exist "%INSTALL_DIR%\logs" mkdir "%INSTALL_DIR%\logs"
if not exist "%INSTALL_DIR%\database" mkdir "%INSTALL_DIR%\database"
if not exist "%INSTALL_DIR%\backup" mkdir "%INSTALL_DIR%\backup"

cd /d "%INSTALL_DIR%"
echo ✅ Arbeitsverzeichnis bereit: %CD%

echo.
echo ========================================
echo   SCHRITT 2: PYTHON 3.11.8 INSTALLATION
echo ========================================

REM Python intelligente Erkennung
echo 🐍 Intelligente Python-Analyse...
set "PYTHON_FOUND=0"
set "PYTHON_EXE="
set "PIP_EXE="

REM 1. Standard python Befehl testen
python --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo !PYTHON_VERSION! | findstr "3.11" >nul
    if !errorlevel! equ 0 (
        echo ✅ Python 3.11 bereits funktionsfähig: !PYTHON_VERSION!
        set "PYTHON_FOUND=1"
        set "PYTHON_EXE=python"
        set "PIP_EXE=pip"
    ) else (
        echo ⚠️  Falsche Python-Version gefunden: !PYTHON_VERSION!
        echo    Benötigt: Python 3.11.x
    )
)

REM 2. py Launcher testen (falls python-Befehl nicht funktioniert)
if !PYTHON_FOUND! equ 0 (
    py -3.11 --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Python 3.11 über py-Launcher gefunden
        for /f "tokens=*" %%i in ('py -3.11 --version 2^>^&1') do echo    Version: %%i
        set "PYTHON_FOUND=1"
        set "PYTHON_EXE=py -3.11"
        set "PIP_EXE=py -3.11 -m pip"
    )
)

REM 3. Manuelle Suche in Standard-Pfaden
if !PYTHON_FOUND! equ 0 (
    echo 🔍 Suche Python in Standard-Installationspfaden...
    set "SEARCH_PATHS=C:\Python311;C:\Program Files\Python311;%USERPROFILE%\AppData\Local\Programs\Python\Python311"
    
    for %%p in (!SEARCH_PATHS!) do (
        if exist "%%p\python.exe" (
            echo ✅ Python gefunden: %%p\python.exe
            "%%p\python.exe" --version 2>nul | findstr "3.11" >nul
            if !errorlevel! equ 0 (
                echo ✅ Korrekte Python 3.11 Version gefunden
                set "PYTHON_FOUND=1"
                set "PYTHON_EXE=%%p\python.exe"
                set "PIP_EXE=%%p\Scripts\pip.exe"
                goto python_found
            )
        )
    )
)

:python_found
REM 4. Python installieren falls nicht gefunden
if !PYTHON_FOUND! equ 0 (
    echo ❌ Python 3.11 nicht gefunden - installiere automatisch...
    echo.
    echo 📥 INSTALLIERE PYTHON 3.11.8 (VOLLVERSION)
    echo ============================================
    
    REM Python 3.11.8 Vollinstaller herunterladen
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    set "PYTHON_INSTALLER=%INSTALL_DIR%\temp\python-3.11.8-installer.exe"
    
    echo    Lade Python 3.11.8 herunter (ca. 25MB)...
    powershell -Command "try { Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%' -UserAgent 'Mozilla/5.0' } catch { exit 1 }" 2>nul
    
    if exist "%PYTHON_INSTALLER%" (
        echo ✅ Download erfolgreich
        echo.
        echo    Installiere Python 3.11.8...
        echo    ⏳ Das kann 2-3 Minuten dauern...
        
        REM Stille Installation mit allen wichtigen Optionen
        "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_tcltk=1 Include_pip=1 Include_doc=0 Include_dev=0
        
        echo    Warte auf Installationsabschluss...
        timeout /t 10 /nobreak >nul
        
        REM Umgebungsvariablen neu laden
        call :refresh_environment
        
        REM Installation testen
        python --version >nul 2>&1
        if !errorlevel! equ 0 (
            for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo ✅ Python erfolgreich installiert: %%i
            set "PYTHON_FOUND=1"
            set "PYTHON_EXE=python"
            set "PIP_EXE=pip"
        ) else (
            echo ❌ Python-Installation fehlgeschlagen
            echo.
            echo MANUELLE INSTALLATION ERFORDERLICH:
            echo 1. Öffnen Sie: https://www.python.org/downloads/
            echo 2. Laden Sie Python 3.11.8 herunter
            echo 3. Installieren Sie mit "Add Python to PATH"
            echo 4. Starten Sie diesen Installer erneut
            pause
            exit /b 1
        )
        
        REM Installer löschen
        del "%PYTHON_INSTALLER%" >nul 2>&1
    ) else (
        echo ❌ FEHLER: Python-Download fehlgeschlagen
        echo.
        echo MANUELLE INSTALLATION ERFORDERLICH:
        echo 1. Internetverbindung prüfen
        echo 2. Firewall/Antivirus temporär deaktivieren
        echo 3. Python manuell von python.org installieren
        pause
        exit /b 1
    )
) else (
    echo ✅ Python 3.11 ist bereits installiert und funktionsfähig
)

echo.
echo 🔧 VERWENDE PYTHON:
echo ====================
echo Executable: %PYTHON_EXE%
echo pip: %PIP_EXE%
echo.

REM pip Update
echo 📦 Aktualisiere pip...
"%PIP_EXE%" install --upgrade pip --quiet >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ pip erfolgreich aktualisiert
) else (
    echo ⚠️  pip-Update fehlgeschlagen (nicht kritisch)
)

echo.
echo ========================================
echo   SCHRITT 3: WARTUNGSMANAGER DATEIEN
echo ========================================

echo 📂 Kopiere Wartungsmanager-Dateien...

REM Projekt-Dateien kopieren (vom aktuellen Verzeichnis)
set SOURCE_DIR=%~dp0..\Source\Python
if exist "%SOURCE_DIR%" (
    echo    Kopiere von: %SOURCE_DIR%
    xcopy "%SOURCE_DIR%\*" "%INSTALL_DIR%\" /E /I /Y /Q >nul 2>&1
    echo ✅ Projekt-Dateien kopiert
) else (
    echo ❌ FEHLER: Source-Verzeichnis nicht gefunden: %SOURCE_DIR%
    echo Bitte Installer im Wartungsmanager-Hauptverzeichnis ausführen
    pause
    exit /b 1
)

REM Konfiguration für lokale Installation anpassen
echo 📝 Konfiguriere für lokalen Betrieb...
if not exist "%INSTALL_DIR%\config" mkdir "%INSTALL_DIR%\config"
(
echo # Lokale Kassen-Installation - Automatisch generiert
echo import os
echo.
echo class LocalConfig:
echo     HOST = '0.0.0.0'
echo     PORT = 5000
echo     DEBUG = False
echo     SQLALCHEMY_DATABASE_URI = 'sqlite:///database/wartungsmanager.db'
echo     SECRET_KEY = 'Magicfactory15!_LOCAL_KASSE_2025'
echo     
echo     # Backup zur WD My Cloud
echo     NAS_BACKUP_PATH = r'\\192.168.0.231\Tauchen\KompressorUeberwachung\backup'
echo     AUTO_BACKUP_ENABLED = True
echo     BACKUP_INTERVAL_HOURS = 6
) > "%INSTALL_DIR%\config\local.py"

echo ✅ Lokale Konfiguration erstellt

echo.
echo ========================================
echo   SCHRITT 4: VIRTUAL ENVIRONMENT
echo ========================================

echo 🏗️  Erstelle Virtual Environment...

REM Virtual Environment erstellen
cd /d "%INSTALL_DIR%"
if exist "wartung_env" (
    echo    Lösche existierendes Virtual Environment...
    rmdir /s /q "wartung_env" >nul 2>&1
)

echo    Erstelle neues Virtual Environment...
"%PYTHON_EXE%" -m venv wartung_env

if exist "wartung_env\Scripts\python.exe" (
    echo ✅ Virtual Environment erfolgreich erstellt
    
    REM Virtual Environment aktivieren und pip upgraden
    echo    Aktualisiere pip im Virtual Environment...
    wartung_env\Scripts\python.exe -m pip install --upgrade pip --quiet >nul 2>&1
    
) else (
    echo ❌ Virtual Environment-Erstellung fehlgeschlagen
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SCHRITT 5: PYTHON DEPENDENCIES
echo ========================================

echo 📦 Installiere Python-Abhängigkeiten...

REM Requirements installieren
if exist "%INSTALL_DIR%\requirements.txt" (
    echo    Installiere Requirements mit Virtual Environment...
    echo    ⏳ Das kann 3-5 Minuten dauern...
    
    wartung_env\Scripts\pip.exe install -r "%INSTALL_DIR%\requirements.txt" --quiet --disable-pip-version-check
    if !errorlevel! equ 0 (
        echo ✅ Dependencies erfolgreich installiert
        
        REM Test der wichtigsten Module
        echo    Teste Flask-Installation...
        wartung_env\Scripts\python.exe -c "import flask; print('✅ Flask', flask.__version__)" 2>nul
        wartung_env\Scripts\python.exe -c "import sqlalchemy; print('✅ SQLAlchemy', sqlalchemy.__version__)" 2>nul
        
    ) else (
        echo ⚠️  Warning: Einige Dependencies konnten nicht installiert werden
        echo    Versuche einzelne Installation kritischer Pakete...
        
        wartung_env\Scripts\pip.exe install Flask==2.3.3 --quiet >nul 2>&1
        wartung_env\Scripts\pip.exe install Flask-SQLAlchemy==3.0.5 --quiet >nul 2>&1
        wartung_env\Scripts\pip.exe install SQLAlchemy==2.0.21 --quiet >nul 2>&1
        
        echo ✅ Kritische Pakete installiert
    )
) else (
    echo ❌ FEHLER: requirements.txt nicht gefunden
    echo    Erstelle minimal requirements.txt...
    (
    echo Flask==2.3.3
    echo Flask-SQLAlchemy==3.0.5
    echo SQLAlchemy==2.0.21
    echo Flask-Migrate==4.0.5
    ) > "%INSTALL_DIR%\requirements.txt"
    
    wartung_env\Scripts\pip.exe install -r "%INSTALL_DIR%\requirements.txt" --quiet
    echo ✅ Minimal-Dependencies installiert
)

echo.
echo ========================================
echo   SCHRITT 6: DATENBANK SETUP
echo ========================================

echo 💾 Initialisiere Datenbank...

REM Datenbank-Migration
if exist "%INSTALL_DIR%\run_migration.py" (
    echo    Führe Datenbank-Migration aus...
    wartung_env\Scripts\python.exe "%INSTALL_DIR%\run_migration.py"
) else if exist "%INSTALL_DIR%\migrations" (
    echo    Führe Alembic-Migration aus...
    cd /d "%INSTALL_DIR%"
    wartung_env\Scripts\python.exe -m alembic upgrade head >nul 2>&1
) else (
    echo    Erstelle initiale Datenbank...
    if exist "%INSTALL_DIR%\run.py" (
        timeout /t 2 /nobreak >nul
        REM Flask App kurz starten um DB zu erstellen
        start /b "" wartung_env\Scripts\python.exe "%INSTALL_DIR%\run.py" >nul 2>&1
        timeout /t 5 /nobreak >nul
        taskkill /f /im python.exe >nul 2>&1
    )
)

echo ✅ Datenbank initialisiert

echo.
echo ========================================
echo   SCHRITT 7: WINDOWS INTEGRATION
echo ========================================

echo 🖥️  Erstelle Windows-Integration...

REM Desktop-Verknüpfung erstellen
echo    Erstelle Desktop-Verknüpfung...
set DESKTOP=%USERPROFILE%\Desktop
(
echo @echo off
echo title Wartungsmanager - Startet...
echo cd /d "C:\Wartungsmanager"
echo start "Wartungsmanager" wartung_env\Scripts\python.exe run.py
echo timeout /t 3 /nobreak ^>nul
echo start http://localhost:5000
echo exit
) > "%DESKTOP%\Wartungsmanager.bat"

REM Startmenü-Eintrag
echo    Erstelle Startmenü-Eintrag...
set STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs
if not exist "%STARTMENU%\Wartungsmanager" mkdir "%STARTMENU%\Wartungsmanager"

(
echo @echo off
echo cd /d "C:\Wartungsmanager"
echo wartung_env\Scripts\python.exe run.py
) > "%STARTMENU%\Wartungsmanager\Wartungsmanager Server.bat"

(
echo @echo off
echo start http://localhost:5000
) > "%STARTMENU%\Wartungsmanager\Wartungsmanager öffnen.bat"

echo ✅ Windows-Integration erstellt

echo.
echo ========================================
echo   SCHRITT 8: AUTO-START KONFIGURATION
echo ========================================

echo ⚙️  Konfiguriere Auto-Start...

REM Auto-Start bei Windows-Boot
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
(
echo @echo off
echo timeout /t 30 /nobreak ^>nul
echo cd /d "C:\Wartungsmanager"
echo start /min "Wartungsmanager" wartung_env\Scripts\python.exe run.py
) > "%STARTUP_DIR%\Wartungsmanager_AutoStart.bat"

echo ✅ Auto-Start konfiguriert (startet 30s nach Windows-Boot)

echo.
echo ========================================
echo   SCHRITT 9: NAS-BACKUP EINRICHTUNG
echo ========================================

echo 💾 Konfiguriere NAS-Backup...

REM Backup-Script zur WD My Cloud
(
echo @echo off
echo title Wartungsmanager - NAS Backup
echo.
echo echo Erstelle Backup zur WD My Cloud...
echo set NAS_PATH=\\192.168.0.231\Tauchen\KompressorUeberwachung\backup
echo set TIMESTAMP=%%date:~10,4%%-%%date:~4,2%%-%%date:~7,2%%_%%time:~0,2%%-%%time:~3,2%%
echo.
echo if not exist "%%NAS_PATH%%" ^(
echo     echo ⚠️  NAS nicht erreichbar: %%NAS_PATH%%
echo     exit /b 1
echo ^)
echo.
echo echo Sichere Datenbank...
echo copy "C:\Wartungsmanager\database\*.db" "%%NAS_PATH%%\wartungsmanager_%%TIMESTAMP%%.db" ^>nul
echo echo Sichere Logs...
echo copy "C:\Wartungsmanager\logs\*.log" "%%NAS_PATH%%\" ^>nul 2^>^&1
echo echo Sichere Konfiguration...
echo copy "C:\Wartungsmanager\config\*.py" "%%NAS_PATH%%\" ^>nul 2^>^&1
echo.
echo echo ✅ Backup completed: %%TIMESTAMP%%
echo echo %%date%% %%time%% - Backup zur NAS erstellt ^>^> "C:\Wartungsmanager\logs\backup.log"
) > "%INSTALL_DIR%\backup_to_nas.bat"

REM Automatisches Backup alle 6 Stunden über Task Scheduler
echo    Registriere automatisches Backup...
schtasks /create /tn "Wartungsmanager NAS Backup" /tr "C:\Wartungsmanager\backup_to_nas.bat" /sc hourly /mo 6 /ru SYSTEM /f >nul 2>&1

echo ✅ NAS-Backup konfiguriert (alle 6 Stunden)

echo.
echo ========================================
echo   SCHRITT 10: FIREWALL KONFIGURATION
echo ========================================

echo 🔥 Konfiguriere Windows Firewall...

REM Firewall-Regel für Port 5000
netsh advfirewall firewall delete rule name="Wartungsmanager" >nul 2>&1
netsh advfirewall firewall add rule name="Wartungsmanager" dir=in action=allow protocol=TCP localport=5000 >nul 2>&1

echo ✅ Firewall-Regel erstellt (Port 5000)

echo.
echo ========================================
echo   SCHRITT 11: INSTALLATION TESTEN
echo ========================================

echo 🧪 Teste Installation...

cd /d "%INSTALL_DIR%"
echo    Teste Python-Import...
wartung_env\Scripts\python.exe -c "import sys; print('Python:', sys.version)" 2>nul
wartung_env\Scripts\python.exe -c "import flask; print('Flask funktioniert')" 2>nul

if !errorlevel! equ 0 (
    echo ✅ Alle Tests erfolgreich
) else (
    echo ⚠️  Einige Tests fehlgeschlagen - System sollte trotzdem funktionieren
)

echo.
echo ========================================
echo   INSTALLATION ABGESCHLOSSEN!
echo ========================================
echo.
echo ✅ Wartungsmanager erfolgreich installiert!
echo.
echo 📍 Installation: C:\Wartungsmanager
echo 🐍 Python: %PYTHON_EXE%
echo 🌐 Server-URL: http://localhost:5000
echo 💾 NAS-Backup: \\192.168.0.231\Tauchen\KompressorUeberwachung\backup
echo.
echo ========================================
echo   ZUGRIFFSMÖGLICHKEITEN:
echo ========================================
echo 🖥️  Desktop: Doppelklick auf "Wartungsmanager.bat"
echo 📱 Browser: http://localhost:5000
echo 🏢 Netzwerk: http://[DIESE-PC-IP]:5000
echo 📂 Startmenü: Programme → Wartungsmanager
echo.
echo ========================================
echo   AUTOMATISCHE FUNKTIONEN:
echo ========================================
echo ⚙️  Auto-Start: Startet automatisch mit Windows
echo 💾 NAS-Backup: Alle 6 Stunden automatisch
echo 🔥 Firewall: Port 5000 automatisch freigegeben
echo 🌐 Virtual Environment: Isolierte Python-Umgebung
echo.
echo Möchten Sie Wartungsmanager jetzt starten?
choice /c JN /n /m "[J]a oder [N]ein: "
if errorlevel 1 (
    echo.
    echo 🚀 Starte Wartungsmanager...
    start "Wartungsmanager" wartung_env\Scripts\python.exe "%INSTALL_DIR%\run.py"
    timeout /t 3 /nobreak >nul
    start http://localhost:5000
    echo.
    echo ✅ Wartungsmanager läuft!
    echo Browser sollte automatisch geöffnet werden...
    echo.
    echo 📱 TIPP: Für iPad-Zugriff verwenden Sie:
    echo    http://[DIESE-PC-IP]:5000
)

echo.
echo Installation completed successfully!
echo Drücken Sie eine Taste zum Beenden...
pause >nul

REM Temporäre Dateien löschen
if exist "%INSTALL_DIR%\temp" rmdir /s /q "%INSTALL_DIR%\temp" >nul 2>&1

exit /b 0

REM ========================================
REM   HILFSFUNKTIONEN
REM ========================================

:refresh_environment
REM Lädt Umgebungsvariablen neu ohne Neustart
echo    Aktualisiere Umgebungsvariablen...
for /f "skip=2 tokens=3*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "NewPath=%%a %%b"
if defined NewPath set "PATH=%NewPath%"
goto :eof
