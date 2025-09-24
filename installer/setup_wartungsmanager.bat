@echo off
title Wartungsmanager - Vollautomatische Installation
color 0A
mode con: cols=80 lines=30

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
echo   WARTUNGSMANAGER INSTALLER v1.0
echo ========================================
echo   Vollautomatische Installation
echo   für Kassenrechner-System
echo ========================================
echo.
echo 📦 Installation wird vorbereitet...
echo 🖥️  Zielrechner: Kassenrechner (Server-Modus)
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
echo   SCHRITT 2: PYTHON INSTALLATION
echo ========================================

REM Python-Version prüfen
echo 🐍 Prüfe Python-Installation...
python --version >nul 2>&1
if %errorlevel% EQU 0 (
    echo ✅ Python bereits installiert
    python --version
) else (
    echo 📥 Python nicht gefunden - installiere Python 3.11.8 (VOLLVERSION)...
    
    REM Python 3.11.8 Vollinstaller herunterladen
    set PYTHON_URL=https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
    set PYTHON_INSTALLER=%INSTALL_DIR%\temp\python-3.11.8-installer.exe
    
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
        for /f "skip=2 tokens=3*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "PATH=%%a %%b"
        
        REM Installation testen
        python --version >nul 2>&1
        if !errorlevel! equ 0 (
            for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo ✅ Python erfolgreich installiert: %%i
        ) else (
            echo ❌ Python-Installation fehlgeschlagen
            echo Bitte Python manuell von python.org installieren und "Add Python to PATH" aktivieren
            pause
            exit /b 1
        )
        
        REM Installer löschen
        del "%PYTHON_INSTALLER%" >nul 2>&1
        echo ✅ Python 3.11.8 Vollinstallation erfolgreich abgeschlossen
    ) else (
        echo ❌ FEHLER: Python-Download fehlgeschlagen
        echo Installieren Sie Python manuell von python.org
        pause
        exit /b 1
    )
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
echo   SCHRITT 4: PYTHON DEPENDENCIES
echo ========================================

echo 📦 Installiere Python-Abhängigkeiten...

REM Python-Pfad ermitteln (für RICHTIGE Installation)
set PYTHON_EXE=python
set PIP_EXE=pip

REM Fallback: Suche in Standard-Pfaden falls python-Befehl nicht funktioniert
python --version >nul 2>&1
if !errorlevel! neq 0 (
    if exist "C:\Python311\python.exe" (
        set PYTHON_EXE=C:\Python311\python.exe
        set PIP_EXE=C:\Python311\Scripts\pip.exe
    ) else if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe" (
        set PYTHON_EXE=%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe
        set PIP_EXE=%USERPROFILE%\AppData\Local\Programs\Python\Python311\Scripts\pip.exe
    )
)

echo    Verwende Python: %PYTHON_EXE%
echo    Verwende pip: %PIP_EXE%
echo    Python-Version: 
%PYTHON_EXE% --version 2>nul

REM Requirements installieren
if exist "%INSTALL_DIR%\requirements.txt" (
    echo    Installiere Requirements...
    "%PIP_EXE%" install -r "%INSTALL_DIR%\requirements.txt" --quiet --disable-pip-version-check
    if %errorlevel% EQU 0 (
        echo ✅ Dependencies erfolgreich installiert
    ) else (
        echo ⚠️  Warning: Einige Dependencies konnten nicht installiert werden
        echo    System sollte trotzdem funktionieren
    )
) else (
    echo ⚠️  Warning: requirements.txt nicht gefunden
)

echo.
echo ========================================
echo   SCHRITT 5: DATENBANK SETUP
echo ========================================

echo 💾 Initialisiere Datenbank...

REM Datenbank-Migration
if exist "%INSTALL_DIR%\run_migration.py" (
    echo    Führe Datenbank-Migration aus...
    "%PYTHON_EXE%" "%INSTALL_DIR%\run_migration.py"
) else if exist "%INSTALL_DIR%\migrations" (
    echo    Führe Alembic-Migration aus...
    cd /d "%INSTALL_DIR%"
    "%PYTHON_EXE%" -m alembic upgrade head
)

echo ✅ Datenbank initialisiert

echo.
echo ========================================
echo   SCHRITT 6: WINDOWS INTEGRATION
echo ========================================

echo 🖥️  Erstelle Windows-Integration...

REM Desktop-Verknüpfung erstellen
echo    Erstelle Desktop-Verknüpfung...
set DESKTOP=%USERPROFILE%\Desktop
(
echo @echo off
echo title Wartungsmanager - Startet...
echo cd /d "C:\Wartungsmanager"
echo start "Wartungsmanager" python run.py
echo timeout /t 2 /nobreak ^>nul
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
echo python run.py
) > "%STARTMENU%\Wartungsmanager\Wartungsmanager Server.bat"

(
echo @echo off
echo start http://localhost:5000
) > "%STARTMENU%\Wartungsmanager\Wartungsmanager öffnen.bat"

echo ✅ Windows-Integration erstellt

echo.
echo ========================================
echo   SCHRITT 7: AUTO-START KONFIGURATION
echo ========================================

echo ⚙️  Konfiguriere Auto-Start...

REM Auto-Start bei Windows-Boot
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
(
echo @echo off
echo timeout /t 30 /nobreak ^>nul
echo cd /d "C:\Wartungsmanager"
echo start /min "Wartungsmanager" python run.py
) > "%STARTUP_DIR%\Wartungsmanager_AutoStart.bat"

echo ✅ Auto-Start konfiguriert (startet 30s nach Windows-Boot)

echo.
echo ========================================
echo   SCHRITT 8: NAS-BACKUP EINRICHTUNG
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
echo   SCHRITT 9: FIREWALL KONFIGURATION
echo ========================================

echo 🔥 Konfiguriere Windows Firewall...

REM Firewall-Regel für Port 5000
netsh advfirewall firewall delete rule name="Wartungsmanager" >nul 2>&1
netsh advfirewall firewall add rule name="Wartungsmanager" dir=in action=allow protocol=TCP localport=5000 >nul 2>&1

echo ✅ Firewall-Regel erstellt (Port 5000)

echo.
echo ========================================
echo   SCHRITT 10: UNINSTALLER ERSTELLEN
echo ========================================

echo 🗑️  Erstelle Uninstaller...

(
echo @echo off
echo title Wartungsmanager - Uninstaller
echo.
echo if "%%1"=="silent" goto uninstall
echo.
echo echo Wartungsmanager Uninstaller
echo echo ===========================
echo echo.
echo echo Möchten Sie Wartungsmanager wirklich deinstallieren?
echo choice /c JN /n /m "[J]a oder [N]ein: "
echo if errorlevel 2 exit /b
echo.
echo :uninstall
echo echo Stoppe Wartungsmanager...
echo taskkill /f /im python.exe ^>nul 2^>^&1
echo.
echo echo Entferne Auto-Start...
echo del "%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Startup\Wartungsmanager_AutoStart.bat" ^>nul 2^>^&1
echo.
echo echo Entferne Task Scheduler...
echo schtasks /delete /tn "Wartungsmanager NAS Backup" /f ^>nul 2^>^&1
echo.
echo echo Entferne Firewall-Regel...
echo netsh advfirewall firewall delete rule name="Wartungsmanager" ^>nul 2^>^&1
echo.
echo echo Entferne Desktop-Verknüpfung...
echo del "%%USERPROFILE%%\Desktop\Wartungsmanager.bat" ^>nul 2^>^&1
echo.
echo echo Entferne Startmenü...
echo rmdir /s /q "%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Wartungsmanager" ^>nul 2^>^&1
echo.
echo echo Entferne Programm-Dateien...
echo rmdir /s /q "C:\Wartungsmanager" ^>nul 2^>^&1
echo.
echo echo ✅ Wartungsmanager erfolgreich deinstalliert
echo if "%%1" NEQ "silent" pause
) > "%INSTALL_DIR%\uninstall.bat"

echo ✅ Uninstaller erstellt

echo.
echo ========================================
echo   INSTALLATION ABGESCHLOSSEN!
echo ========================================
echo.
echo ✅ Wartungsmanager erfolgreich installiert!
echo.
echo 📍 Installation: C:\Wartungsmanager
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
echo.
echo Möchten Sie Wartungsmanager jetzt starten?
choice /c JN /n /m "[J]a oder [N]ein: "
if errorlevel 1 (
    echo.
    echo 🚀 Starte Wartungsmanager...
    start "Wartungsmanager" python "%INSTALL_DIR%\run.py"
    timeout /t 3 /nobreak >nul
    start http://localhost:5000
    echo.
    echo ✅ Wartungsmanager läuft!
    echo Browser sollte automatisch geöffnet werden...
)

echo.
echo Installation completed successfully!
echo Drücken Sie eine Taste zum Beenden...
pause >nul

REM Temporäre Dateien löschen
if exist "%INSTALL_DIR%\temp" rmdir /s /q "%INSTALL_DIR%\temp" >nul 2>&1

exit /b 0
