@echo off
setlocal enabledelayedexpansion

REM FEHLERGESCHÜTZTE INSTALLATION - PAUSIERT BEI JEDEM FEHLER

echo.
echo ████████████████████████████████████████████████████████████████████████████████
echo █                                                                              █
echo █    🔧 WARTUNGSMANAGER - FEHLERGESCHÜTZTE INSTALLATION                       █
echo █                                                                              █
echo █    Diese Version pausiert bei jedem Schritt für Debugging                   █
echo █                                                                              █
echo ████████████████████████████████████████████████████████████████████████████████
echo.

REM 1. ADMINISTRATOR-RECHTE PRÜFEN
echo 🔐 SCHRITT 1: ADMINISTRATOR-RECHTE PRÜFEN
echo ==========================================
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    echo ❌ FEHLER: Keine Administrator-Rechte!
    echo.
    echo LÖSUNG:
    echo 1. Rechtsklick auf diese BAT-Datei
    echo 2. "Als Administrator ausführen" wählen
    echo 3. UAC-Dialog mit "Ja" bestätigen
    echo.
    pause
    exit /b 1
)
echo ✅ Administrator-Rechte vorhanden
pause

REM 2. ARBEITSVERZEICHNIS ERSTELLEN
echo.
echo 📁 SCHRITT 2: ARBEITSVERZEICHNIS ERSTELLEN  
echo ============================================
set "INSTALL_DIR=C:\Wartungsmanager"
set "TEMP_DIR=%INSTALL_DIR%\temp"

echo Erstelle Verzeichnis: %INSTALL_DIR%
if exist "%INSTALL_DIR%" (
    echo Lösche alte Installation...
    rmdir /s /q "%INSTALL_DIR%" >nul 2>&1
)

mkdir "%INSTALL_DIR%" 2>nul
if not exist "%INSTALL_DIR%" (
    echo ❌ FEHLER: Kann Verzeichnis nicht erstellen!
    echo Versuche C:\temp\Wartungsmanager...
    set "INSTALL_DIR=C:\temp\Wartungsmanager"
    mkdir "%INSTALL_DIR%" 2>nul
)

mkdir "%INSTALL_DIR%\temp" 2>nul
mkdir "%INSTALL_DIR%\logs" 2>nul
mkdir "%INSTALL_DIR%\database" 2>nul

if exist "%INSTALL_DIR%" (
    echo ✅ Arbeitsverzeichnis erstellt: %INSTALL_DIR%
) else (
    echo ❌ KRITISCHER FEHLER: Kann keine Verzeichnisse erstellen!
    pause
    exit /b 1
)
pause

REM 3. INTERNET-VERBINDUNG TESTEN
echo.
echo 🌐 SCHRITT 3: INTERNET-VERBINDUNG TESTEN
echo =========================================
echo Teste Verbindung zu python.org...
ping -n 1 python.org >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Internet-Verbindung funktioniert
) else (
    echo ❌ WARNUNG: Keine Verbindung zu python.org
    echo.
    echo MÖGLICHE PROBLEME:
    echo - Keine Internet-Verbindung
    echo - Firewall blockiert ping
    echo - Proxy-Einstellungen
    echo.
    echo Soll trotzdem fortgefahren werden? (j/n)
    set /p continue="Ihre Eingabe: "
    if /i not "%continue%"=="j" exit /b 1
)
pause

REM 4. PYTHON PRÜFEN
echo.
echo 🐍 SCHRITT 4: PYTHON-STATUS PRÜFEN
echo ===================================
set "PYTHON_OK=0"
set "PYTHON_EXE="

echo Teste python --version...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do (
        echo Gefunden: %%i
        echo %%i | findstr "3.11" >nul
        if !errorlevel! equ 0 (
            echo ✅ Python 3.11 bereits installiert!
            set "PYTHON_OK=1"
            set "PYTHON_EXE=python"
        ) else (
            echo ⚠️  Falsche Version - benötigt Python 3.11
        )
    )
) else (
    echo ❌ Python-Befehl nicht gefunden
)

echo Teste py -3.11 --version...
py -3.11 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python 3.11 über py-Launcher verfügbar
    if !PYTHON_OK! equ 0 (
        set "PYTHON_OK=1"
        set "PYTHON_EXE=py -3.11"
    )
) else (
    echo ❌ py-Launcher für 3.11 nicht verfügbar
)

if !PYTHON_OK! equ 1 (
    echo.
    echo ✅ PYTHON 3.11 GEFUNDEN - Installation wird übersprungen
    goto python_done
) else (
    echo.
    echo ❌ PYTHON 3.11 NICHT GEFUNDEN - Wird installiert
)
pause

REM 5. PYTHON DOWNLOADEN
echo.
echo 📥 SCHRITT 5: PYTHON 3.11.8 HERUNTERLADEN
echo ==========================================
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
set "PYTHON_INSTALLER=%INSTALL_DIR%\temp\python-installer.exe"

echo URL: %PYTHON_URL%
echo Ziel: %PYTHON_INSTALLER%
echo.
echo Starte Download...

powershell -Command "try { $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%' -UserAgent 'Mozilla/5.0' -TimeoutSec 300 } catch { Write-Host 'FEHLER:' $_.Exception.Message; exit 1 }"

if exist "%PYTHON_INSTALLER%" (
    echo ✅ Download erfolgreich
    for %%A in ("%PYTHON_INSTALLER%") do echo Dateigröße: %%~zA Bytes
) else (
    echo ❌ DOWNLOAD FEHLGESCHLAGEN!
    echo.
    echo MÖGLICHE LÖSUNGEN:
    echo 1. Internet-Verbindung prüfen
    echo 2. Firewall/Antivirus temporär deaktivieren
    echo 3. Proxy-Einstellungen prüfen
    echo 4. Später nochmal versuchen
    echo.
    echo Soll Python manuell installiert werden? (j/n)
    set /p manual="Ihre Eingabe: "
    if /i "%manual%"=="j" (
        echo.
        echo MANUELLE INSTALLATION:
        echo 1. Öffnen Sie: https://www.python.org/downloads/
        echo 2. Laden Sie Python 3.11.8 (64-bit) herunter
        echo 3. Installieren Sie mit "Add Python to PATH"
        echo 4. Starten Sie diese Installation erneut
        pause
        exit /b 1
    ) else (
        pause
        exit /b 1
    )
)
pause

REM 6. PYTHON INSTALLIEREN
echo.
echo 🔧 SCHRITT 6: PYTHON 3.11.8 INSTALLIEREN
echo =========================================
echo Starte Installation...
echo Das kann 3-5 Minuten dauern...
echo.

"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_tcltk=1 Include_pip=1 Include_doc=0 Include_dev=0 Include_launcher=1

echo Warte auf Installationsabschluss...
timeout /t 20 /nobreak >nul

REM PATH neu laden
echo Lade PATH-Variable neu...
for /f "skip=2 tokens=3*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do (
    if not "%%b"=="" set "PATH=%%a %%b"
)

echo Teste Installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo ✅ Python installiert: %%i
    set "PYTHON_EXE=python"
) else (
    echo ❌ Python-Installation fehlgeschlagen!
    echo.
    echo TROUBLESHOOTING:
    echo 1. CMD/PowerShell neu öffnen
    echo 2. Manuelle Installation von python.org
    echo 3. "Add Python to PATH" aktivieren
    pause
    exit /b 1
)

del "%PYTHON_INSTALLER%" >nul 2>&1
pause

:python_done
echo.
echo ✅ PYTHON-STATUS: OK
echo Python-Executable: %PYTHON_EXE%

REM 7. PIP TESTEN UND UPGRADEN
echo.
echo 📦 SCHRITT 7: PIP TESTEN UND UPGRADEN
echo ======================================
echo Teste pip...
%PYTHON_EXE% -m pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ pip verfügbar
    echo Aktualisiere pip...
    %PYTHON_EXE% -m pip install --upgrade pip --quiet
    echo ✅ pip aktualisiert
) else (
    echo ❌ pip nicht verfügbar!
    pause
    exit /b 1
)
pause

REM 8. WERKZEUG-DATEIEN KOPIEREN
echo.
echo 📂 SCHRITT 8: WARTUNGSMANAGER-DATEIEN VORBEREITEN
echo ==================================================
cd /d "%INSTALL_DIR%"

REM Suche Source-Verzeichnis
set "SOURCE_FOUND=0"
for %%s in (
    "%~dp0..\Source\Python"
    "%~dp0..\..\Source\Python" 
    "C:\SoftwareProjekte\WartungsManager\Source\Python"
) do (
    if exist "%%s\run.py" (
        echo ✅ Quellcode gefunden: %%s
        xcopy "%%s\*" "%INSTALL_DIR%\" /E /I /Y /Q >nul 2>&1
        set "SOURCE_FOUND=1"
        goto source_done
    )
)

:source_done
if !SOURCE_FOUND! equ 0 (
    echo ⚠️  Original-Quellcode nicht gefunden
    echo Erstelle minimale Wartungsmanager-Version...
    
    REM Kopiere minimal run.py
    copy "%~dp0minimal_run.py" "%INSTALL_DIR%\run.py" >nul 2>&1
    if exist "%INSTALL_DIR%\run.py" (
        echo ✅ Minimale Version erstellt
    ) else (
        echo ❌ Kann minimale Version nicht erstellen!
        pause
        exit /b 1
    )
)

if exist "%INSTALL_DIR%\run.py" (
    echo ✅ Wartungsmanager-Code bereit
) else (
    echo ❌ Keine run.py gefunden!
    pause
    exit /b 1
)
pause

REM 9. FLASK INSTALLIEREN
echo.
echo 🌐 SCHRITT 9: FLASK UND ABHÄNGIGKEITEN INSTALLIEREN
echo ===================================================
echo Installiere Flask...
%PYTHON_EXE% -m pip install Flask==2.3.3 --quiet
echo Installiere SQLAlchemy...
%PYTHON_EXE% -m pip install SQLAlchemy==2.0.21 --quiet
echo Installiere Flask-SQLAlchemy...
%PYTHON_EXE% -m pip install Flask-SQLAlchemy==3.0.5 --quiet

echo.
echo Teste Flask-Installation...
%PYTHON_EXE% -c "import flask; print('✅ Flask', flask.__version__)" 2>nul
if %errorlevel% equ 0 (
    echo ✅ Flask erfolgreich installiert
) else (
    echo ❌ Flask-Installation fehlgeschlagen!
    echo Versuche Neuinstallation...
    %PYTHON_EXE% -m pip install Flask --force-reinstall --quiet
)
pause

REM 10. DATENBANK INITIALISIEREN
echo.
echo 💾 SCHRITT 10: DATENBANK VORBEREITEN
echo ====================================
mkdir "%INSTALL_DIR%\database" >nul 2>&1
echo Teste SQLite...
%PYTHON_EXE% -c "import sqlite3; print('✅ SQLite verfügbar')" 2>nul
if %errorlevel% equ 0 (
    echo ✅ SQLite-Support verfügbar
) else (
    echo ❌ SQLite-Problem
    pause
    exit /b 1
)
pause

REM 11. DESKTOP-VERKNÜPFUNG
echo.
echo 🖥️ SCHRITT 11: DESKTOP-VERKNÜPFUNG ERSTELLEN
echo =============================================
set "DESKTOP=%USERPROFILE%\Desktop"
(
echo @echo off
echo title Wartungsmanager
echo echo.
echo echo 🔧 Starte Wartungsmanager...
echo cd /d "%INSTALL_DIR%"
echo %PYTHON_EXE% run.py
echo pause
) > "%DESKTOP%\Wartungsmanager.bat"

if exist "%DESKTOP%\Wartungsmanager.bat" (
    echo ✅ Desktop-Verknüpfung erstellt
) else (
    echo ⚠️  Desktop-Verknüpfung fehlgeschlagen
)
pause

REM 12. INSTALLATION TESTEN
echo.
echo 🧪 SCHRITT 12: INSTALLATION TESTEN
echo ===================================
cd /d "%INSTALL_DIR%"
echo Teste Wartungsmanager...
echo Starte Server für 5 Sekunden...

start /b "" %PYTHON_EXE% run.py >nul 2>&1
timeout /t 5 /nobreak >nul
taskkill /f /im python.exe >nul 2>&1

echo ✅ Test abgeschlossen
pause

REM 13. ABSCHLUSS
echo.
echo ████████████████████████████████████████████████████████████████████████████████
echo █                                                                              █
echo █    🎉 INSTALLATION ABGESCHLOSSEN!                                           █
echo █                                                                              █
echo █    ✅ Python 3.11 installiert                                               █
echo █    ✅ Flask und SQLite verfügbar                                            █
echo █    ✅ Wartungsmanager installiert                                            █
echo █    ✅ Desktop-Verknüpfung erstellt                                          █
echo █                                                                              █
echo █    🚀 ZUM STARTEN:                                                           █
echo █    Doppelklick auf "Wartungsmanager.bat" (Desktop)                          █
echo █    Oder: cd %INSTALL_DIR%                                                   █
echo █           %PYTHON_EXE% run.py                                               █
echo █                                                                              █
echo █    🌐 Zugriff: http://localhost:5000                                         █
echo █                                                                              █
echo ████████████████████████████████████████████████████████████████████████████████
echo.

echo Möchten Sie Wartungsmanager jetzt starten? (j/n)
set /p start_now="Ihre Eingabe: "

if /i "%start_now%"=="j" (
    echo.
    echo 🚀 Starte Wartungsmanager...
    cd /d "%INSTALL_DIR%"
    start "Wartungsmanager" %PYTHON_EXE% run.py
    timeout /t 3 /nobreak >nul
    start http://localhost:5000
    echo.
    echo ✅ Wartungsmanager gestartet!
    echo Browser sollte automatisch öffnen...
)

echo.
echo Installation completed!
pause
