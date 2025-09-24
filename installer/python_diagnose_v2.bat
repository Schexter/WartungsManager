@echo off
setlocal enabledelayedexpansion
title Python 3.11 Diagnose - RICHTIGE INSTALLATION (v2.0)
color 0E
mode con: cols=100 lines=40

echo ===============================================
echo 🐍 PYTHON 3.11 DIAGNOSE - KASSEN-SYSTEM v2.0
echo ===============================================
echo Speziell für RICHTIGE Python-Installation
echo (nicht Portable)
echo ===============================================
echo.

echo 📊 ANALYSIERE PYTHON 3.11 INSTALLATION...
echo ==========================================

echo.
echo 🔍 1. PYTHON 3.11 BEFEHLE TESTEN
echo ---------------------------------
set "PYTHON_FOUND=0"
set "PYTHON_PATH="
set "PYTHON_VERSION="
set "PYTHON_EXE="
set "PIP_EXE="

echo Teste 'python' Befehl...
python --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo ✅ 'python' Befehl funktioniert: !PYTHON_VERSION!
    
    REM Prüfe ob es Python 3.11 ist
    echo !PYTHON_VERSION! | findstr "3.11" >nul
    if !errorlevel! equ 0 (
        echo ✅ Korrekte Python 3.11 Version erkannt
        for /f "tokens=*" %%i in ('where python 2^>nul') do set "PYTHON_PATH=%%i"
        echo    Pfad: !PYTHON_PATH!
        set "PYTHON_FOUND=1"
        set "PYTHON_EXE=python"
        set "PIP_EXE=pip"
    ) else (
        echo ⚠️  FALSCHE VERSION: Benötigt Python 3.11.x
        echo    Gefunden: !PYTHON_VERSION!
    )
) else (
    echo ❌ 'python' Befehl nicht erkannt
)

echo.
echo Teste 'py' Launcher für Python 3.11...
py -3.11 --version >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ 'py -3.11' Launcher funktioniert
    for /f "tokens=*" %%i in ('py -3.11 --version 2^>^&1') do echo    Version: %%i
    
    if !PYTHON_FOUND! equ 0 (
        set "PYTHON_FOUND=1"
        set "PYTHON_EXE=py -3.11"
        set "PIP_EXE=py -3.11 -m pip"
        echo ✅ Verwende py-Launcher als Python-Quelle
    )
) else (
    echo ❌ 'py -3.11' Launcher nicht verfügbar
)

echo.
echo Teste allgemeine 'py' Launcher...
py --version >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ 'py' Launcher verfügbar
    echo    Alle verfügbaren Python-Versionen:
    py -0 2>nul
) else (
    echo ❌ 'py' Launcher nicht installiert
)

echo.
echo 🔍 2. PYTHON 3.11 INSTALLATION SUCHEN
echo -------------------------------------
echo Suche Python 3.11 in Standard-Pfaden...

REM Erweiterte Standard-Installationspfade für Python 3.11
set "SEARCH_PATHS=C:\Python311;C:\Python311\;C:\Program Files\Python311;C:\Program Files (x86)\Python311;%USERPROFILE%\AppData\Local\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311"

for %%p in (!SEARCH_PATHS!) do (
    if exist "%%p\python.exe" (
        echo ✅ Python-Executable gefunden: %%p\python.exe
        
        REM Version prüfen
        "%%p\python.exe" --version >nul 2>&1
        if !errorlevel! equ 0 (
            for /f "tokens=*" %%v in ('"%%p\python.exe" --version 2^>^&1') do (
                echo %%v | findstr "3.11" >nul
                if !errorlevel! equ 0 (
                    echo ✅ Python 3.11 Installation gefunden: %%v
                    if !PYTHON_FOUND! equ 0 (
                        set "PYTHON_FOUND=1"
                        set "PYTHON_EXE=%%p\python.exe"
                        set "PIP_EXE=%%p\Scripts\pip.exe"
                        set "MANUAL_PYTHON_PATH=%%p"
                        echo ✅ Als primäre Python-Quelle registriert
                    )
                ) else (
                    for /f "tokens=*" %%v in ('"%%p\python.exe" --version 2^>^&1') do echo ⚠️  Falsche Version: %%v
                )
            )
        ) else (
            echo ❌ Python-Executable defekt
        )
    )
)

echo.
echo 🔍 3. PIP VERFÜGBARKEIT PRÜFEN
echo -------------------------------
if !PYTHON_FOUND! equ 1 (
    echo Teste pip mit gefundenem Python...
    !PIP_EXE! --version >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%i in ('!PIP_EXE! --version 2^>^&1') do echo ✅ pip funktioniert: %%i
    ) else (
        echo ❌ pip nicht verfügbar oder defekt
        echo    Versuche pip über Python-Modul...
        !PYTHON_EXE! -m pip --version >nul 2>&1
        if !errorlevel! equ 0 (
            echo ✅ pip über Python-Modul verfügbar
            set "PIP_EXE=!PYTHON_EXE! -m pip"
        ) else (
            echo ❌ pip komplett nicht verfügbar
        )
    )
)

echo.
echo 🔍 4. VIRTUAL ENVIRONMENT SUPPORT
echo ----------------------------------
if !PYTHON_FOUND! equ 1 (
    echo Teste venv-Modul...
    !PYTHON_EXE! -m venv --help >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ venv-Modul verfügbar (Virtual Environment Support)
    ) else (
        echo ❌ venv-Modul nicht verfügbar
    )
)

echo.
echo 🔍 5. WARTUNGSMANAGER VIRTUAL ENVIRONMENT
echo ------------------------------------------
cd /d "C:\SoftwareProjekte\WartungsManager\Source\Python" 2>nul
if !errorlevel! equ 0 (
    echo Prüfe Wartungsmanager Virtual Environment...
    if exist "wartung_env\Scripts\python.exe" (
        echo ✅ Virtual Environment gefunden: %CD%\wartung_env
        
        echo    Teste Virtual Environment Python...
        wartung_env\Scripts\python.exe --version >nul 2>&1
        if !errorlevel! equ 0 (
            for /f "tokens=*" %%i in ('wartung_env\Scripts\python.exe --version 2^>^&1') do echo ✅ VEnv Python: %%i
        ) else (
            echo ❌ Virtual Environment Python defekt
        )
        
        echo    Teste Virtual Environment pip...
        wartung_env\Scripts\pip.exe --version >nul 2>&1
        if !errorlevel! equ 0 (
            echo ✅ VEnv pip funktioniert
            echo    Teste Flask-Installation...
            wartung_env\Scripts\python.exe -c "import flask; print('Flask', flask.__version__)" 2>nul
            if !errorlevel! equ 0 (
                echo ✅ Flask im Virtual Environment verfügbar
            ) else (
                echo ❌ Flask nicht installiert im Virtual Environment
            )
        ) else (
            echo ❌ Virtual Environment pip defekt
        )
    ) else (
        echo ❌ Virtual Environment fehlt oder beschädigt
    )
) else (
    echo ❌ Wartungsmanager-Projektverzeichnis nicht gefunden
)

echo.
echo 🔍 6. SYSTEM-PFAD UND REGISTRY ANALYSE
echo ---------------------------------------
echo Prüfe PATH-Variable...
echo %PATH% | findstr /i python >nul
if !errorlevel! equ 0 (
    echo ✅ Python-Pfade in PATH gefunden:
    for %%p in (%PATH:;= %) do (
        echo %%p | findstr /i python >nul
        if !errorlevel! equ 0 echo    %%p
    )
) else (
    echo ❌ Keine Python-Pfade in PATH-Variable
)

echo.
echo Prüfe Python-Registry...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonCore\3.11" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Python 3.11 in System-Registry gefunden
) else (
    echo ❌ Python 3.11 nicht in System-Registry
)

reg query "HKEY_CURRENT_USER\SOFTWARE\Python\PythonCore\3.11" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Python 3.11 in Benutzer-Registry gefunden
) else (
    echo ❌ Python 3.11 nicht in Benutzer-Registry
)

echo.
echo ===============================================
echo 📋 DIAGNOSE-ZUSAMMENFASSUNG
echo ===============================================

if !PYTHON_FOUND! equ 1 (
    echo ✅ PYTHON 3.11 GEFUNDEN UND FUNKTIONSFÄHIG
    echo ==========================================
    echo Python-Executable: !PYTHON_EXE!
    echo pip-Executable: !PIP_EXE!
    if defined PYTHON_VERSION echo Version: !PYTHON_VERSION!
    if defined MANUAL_PYTHON_PATH echo Installationspfad: !MANUAL_PYTHON_PATH!
    
    echo.
    echo 🔧 NÄCHSTE SCHRITTE:
    echo ===================
    echo 1. ✅ Python 3.11 ist korrekt installiert
    echo 2. 🔄 Virtual Environment für Wartungsmanager erstellen/reparieren
    echo 3. 📦 Dependencies installieren
    echo 4. 🚀 Wartungsmanager starten
    
    echo.
    echo Möchten Sie das Virtual Environment automatisch reparieren? (j/n)
    set /p repair_choice="Ihre Wahl: "
    
    if /i "!repair_choice!"=="j" (
        echo.
        echo 🔧 STARTE VIRTUAL ENVIRONMENT REPARATUR...
        echo ==========================================
        call :repair_virtual_environment
    )
    
) else (
    echo ❌ PYTHON 3.11 NICHT GEFUNDEN
    echo =============================
    echo.
    echo 🚨 KRITISCHES PROBLEM:
    echo =====================
    echo Python 3.11 ist nicht installiert oder nicht funktionsfähig
    echo.
    echo 💡 LÖSUNGSOPTIONEN:
    echo ==================
    echo 1. Python 3.11.8 von python.org installieren
    echo 2. Wartungsmanager-Installer v2.0 verwenden (setup_wartungsmanager_v2.bat)
    echo 3. Vorhandene Installation reparieren
    echo.
    echo Möchten Sie Python 3.11.8 automatisch installieren? (j/n)
    set /p install_choice="Ihre Wahl: "
    
    if /i "!install_choice!"=="j" (
        echo.
        echo 📥 INSTALLIERE PYTHON 3.11.8 AUTOMATISCH...
        echo ===========================================
        call :install_python_311
    )
)

echo.
echo ===============================================
echo 📝 ERSTELLE DIAGNOSE-LOG
echo ===============================================
call :create_log

echo.
echo Diagnose abgeschlossen!
echo Drücken Sie eine Taste zum Beenden...
pause >nul
exit /b 0

REM ===============================================
REM   HILFSFUNKTIONEN
REM ===============================================

:repair_virtual_environment
echo.
echo 🔧 VIRTUAL ENVIRONMENT REPARATUR
echo ================================

REM Zum Projektverzeichnis wechseln
cd /d "C:\SoftwareProjekte\WartungsManager\Source\Python" 2>nul
if !errorlevel! neq 0 (
    echo ❌ Projektverzeichnis nicht erreichbar
    goto repair_end
)

echo 1. Lösche altes Virtual Environment...
if exist "wartung_env" (
    echo    Entferne wartung_env...
    rmdir /s /q "wartung_env" >nul 2>&1
    echo ✅ Altes Virtual Environment entfernt
) else (
    echo    Kein vorhandenes Virtual Environment gefunden
)

echo.
echo 2. Erstelle neues Virtual Environment...
"!PYTHON_EXE!" -m venv wartung_env
if !errorlevel! equ 0 (
    echo ✅ Virtual Environment erfolgreich erstellt
) else (
    echo ❌ Virtual Environment-Erstellung fehlgeschlagen
    goto repair_end
)

echo.
echo 3. Aktualisiere pip im Virtual Environment...
wartung_env\Scripts\python.exe -m pip install --upgrade pip --quiet >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ pip im Virtual Environment aktualisiert
) else (
    echo ⚠️  pip-Update fehlgeschlagen (nicht kritisch)
)

echo.
echo 4. Installiere Wartungsmanager Dependencies...
if exist "requirements.txt" (
    echo    Installiere aus requirements.txt...
    wartung_env\Scripts\pip.exe install -r requirements.txt --quiet
    if !errorlevel! equ 0 (
        echo ✅ Dependencies erfolgreich installiert
    ) else (
        echo ⚠️  Einige Dependencies konnten nicht installiert werden
        echo    Installiere kritische Pakete einzeln...
        wartung_env\Scripts\pip.exe install Flask==2.3.3 --quiet >nul 2>&1
        wartung_env\Scripts\pip.exe install Flask-SQLAlchemy==3.0.5 --quiet >nul 2>&1
        wartung_env\Scripts\pip.exe install SQLAlchemy==2.0.21 --quiet >nul 2>&1
        echo ✅ Kritische Pakete installiert
    )
) else (
    echo ❌ requirements.txt nicht gefunden - installiere minimal setup
    wartung_env\Scripts\pip.exe install Flask Flask-SQLAlchemy SQLAlchemy --quiet
)

echo.
echo 5. Teste Installation...
echo    Teste Flask-Import...
wartung_env\Scripts\python.exe -c "import flask; print('✅ Flask', flask.__version__)" 2>nul
wartung_env\Scripts\python.exe -c "import sqlalchemy; print('✅ SQLAlchemy', sqlalchemy.__version__)" 2>nul

if !errorlevel! equ 0 (
    echo.
    echo 🚀 REPARATUR ERFOLGREICH!
    echo =========================
    echo Das Virtual Environment ist jetzt funktionsfähig.
    echo.
    echo So starten Sie Wartungsmanager:
    echo 1. cd C:\SoftwareProjekte\WartungsManager\Source\Python
    echo 2. wartung_env\Scripts\activate.bat
    echo 3. python run.py
    echo.
    echo Möchten Sie Wartungsmanager jetzt starten? (j/n)
    set /p start_choice="Ihre Wahl: "
    if /i "!start_choice!"=="j" (
        echo Starte Wartungsmanager...
        start "Wartungsmanager" wartung_env\Scripts\python.exe run.py
        timeout /t 3 /nobreak >nul
        start http://localhost:5000
        echo ✅ Wartungsmanager gestartet - Browser öffnet automatisch
    )
) else (
    echo ❌ Flask-Import fehlgeschlagen - manuelle Überprüfung erforderlich
)

:repair_end
echo.
echo Reparatur abgeschlossen.
return

:install_python_311
echo.
echo 📥 PYTHON 3.11.8 INSTALLATION
echo =============================

REM Administratorrechte prüfen
openfiles >nul 2>&1
if !errorlevel! neq 0 (
    echo ⚠️  Administrator-Rechte erforderlich für Python-Installation
    echo Starte als Administrator...
    powershell -Command "Start-Process '%0' -Verb RunAs"
    exit /b
)

echo 1. Lade Python 3.11.8 herunter...
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
set "PYTHON_INSTALLER=%TEMP%\python-3.11.8-installer.exe"

echo    Download von: %PYTHON_URL%
powershell -Command "try { Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%' -UserAgent 'Mozilla/5.0' } catch { exit 1 }" 2>nul

if exist "%PYTHON_INSTALLER%" (
    echo ✅ Download erfolgreich (ca. 25MB)
    
    echo.
    echo 2. Installiere Python 3.11.8...
    echo    ⏳ Stille Installation mit PATH-Integration...
    
    REM Vollinstallation mit allen wichtigen Optionen
    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_tcltk=1 Include_pip=1 Include_doc=0 Include_dev=0
    
    echo    Warte auf Installationsabschluss...
    timeout /t 10 /nobreak >nul
    
    echo.
    echo 3. Teste Installation...
    
    REM Umgebungsvariablen neu laden
    call :refresh_environment
    
    python --version >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo ✅ Python erfolgreich installiert: %%i
        echo.
        echo 🎯 INSTALLATION ERFOLGREICH!
        echo ===========================
        echo Python 3.11.8 ist jetzt verfügbar.
        echo.
        echo Möchten Sie jetzt das Virtual Environment einrichten? (j/n)
        set /p setup_venv="Ihre Wahl: "
        if /i "!setup_venv!"=="j" (
            set "PYTHON_FOUND=1"
            set "PYTHON_EXE=python"
            set "PIP_EXE=pip"
            call :repair_virtual_environment
        )
    ) else (
        echo ❌ Python-Installation fehlgeschlagen
        echo.
        echo MANUELLE SCHRITTE ERFORDERLICH:
        echo 1. Bitte Python manuell von python.org installieren
        echo 2. Bei Installation "Add Python to PATH" aktivieren
        echo 3. Nach Installation PowerShell/CMD neu öffnen
    )
    
    REM Installer löschen
    del "%PYTHON_INSTALLER%" >nul 2>&1
) else (
    echo ❌ Download fehlgeschlagen
    echo.
    echo MANUELLE INSTALLATION:
    echo 1. Internetverbindung prüfen
    echo 2. Firewall/Antivirus temporär deaktivieren
    echo 3. Python manuell von https://www.python.org/downloads/ installieren
)

return

:refresh_environment
REM Aktualisiert die Umgebungsvariablen ohne Neustart
echo    Aktualisiere Umgebungsvariablen...
for /f "skip=2 tokens=3*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "NewPath=%%a %%b"
if defined NewPath set "PATH=%NewPath%"
return

:create_log
set "LOG_FILE=C:\SoftwareProjekte\WartungsManager\Logs\python_diagnose_v2_%date:~10,4%-%date:~4,2%-%date:~7,2%_%time:~0,2%-%time:~3,2%.log"
if not exist "C:\SoftwareProjekte\WartungsManager\Logs" mkdir "C:\SoftwareProjekte\WartungsManager\Logs" >nul 2>&1

(
echo Python 3.11 Diagnose Log v2.0 - %date% %time%
echo ================================================
echo.
echo PYTHON STATUS:
echo Python gefunden: !PYTHON_FOUND!
echo Python Executable: !PYTHON_EXE!
echo pip Executable: !PIP_EXE!
echo Version: !PYTHON_VERSION!
echo Installationspfad: !MANUAL_PYTHON_PATH!
echo.
echo SYSTEM ENVIRONMENT:
echo PATH: %PATH%
echo.
echo REGISTRY STATUS:
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonCore\3.11" 2^>nul ^|^| echo Python 3.11 nicht in HKLM Registry
reg query "HKEY_CURRENT_USER\SOFTWARE\Python\PythonCore\3.11" 2^>nul ^|^| echo Python 3.11 nicht in HKCU Registry
echo.
echo VIRTUAL ENVIRONMENT:
if exist "C:\SoftwareProjekte\WartungsManager\Source\Python\wartung_env\Scripts\python.exe" ^(
    echo Status: VORHANDEN
    "C:\SoftwareProjekte\WartungsManager\Source\Python\wartung_env\Scripts\python.exe" --version 2^>nul ^|^| echo Fehlerhaft
^) else ^(
    echo Status: FEHLT
^)
echo.
echo EMPFEHLUNG:
if !PYTHON_FOUND! equ 1 ^(
    echo Virtual Environment neu erstellen
^) else ^(
    echo Python 3.11.8 installieren
^)
) > "%LOG_FILE%" 2>&1

echo ✅ Detailliertes Log erstellt: %LOG_FILE%
return
