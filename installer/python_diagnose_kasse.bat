@echo off
setlocal enabledelayedexpansion
title Python Diagnose - Wartungsmanager Kassen-System
color 0E
mode con: cols=90 lines=35

echo ========================================
echo 🐍 PYTHON DIAGNOSE - KASSEN-SYSTEM
echo ========================================
echo Version: 1.0 - Wartungsmanager Support
echo Datum: %date% %time%
echo ========================================
echo.

echo 📊 ANALYSIERE PYTHON-INSTALLATION...
echo ======================================

echo.
echo 🔍 1. STANDARD PYTHON-BEFEHLE TESTEN
echo ------------------------------------
set "PYTHON_FOUND=0"
set "PYTHON_PATH="
set "PYTHON_VERSION="

echo Teste 'python' Befehl...
python --version >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ 'python' Befehl funktioniert
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo    Version: !PYTHON_VERSION!
    for /f "tokens=*" %%i in ('where python 2^>nul') do set "PYTHON_PATH=%%i"
    echo    Pfad: !PYTHON_PATH!
    set "PYTHON_FOUND=1"
    set "WORKING_PYTHON=python"
) else (
    echo ❌ 'python' Befehl nicht erkannt
)

echo.
echo Teste 'py' Launcher...
py --version >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ 'py' Launcher funktioniert
    py --version
    echo    Verfügbare Versionen:
    py -0 2>nul
    if !PYTHON_FOUND! equ 0 (
        set "PYTHON_FOUND=1"
        set "WORKING_PYTHON=py"
    )
) else (
    echo ❌ 'py' Launcher nicht erkannt
)

echo.
echo 🔍 2. MANUELLE INSTALLATION SUCHEN
echo ----------------------------------
echo Suche Python in Standard-Pfaden...

REM Standard-Installationspfade durchsuchen
set "SEARCH_PATHS=C:\Python311;C:\Python311\;C:\Python312;C:\Program Files\Python311;C:\Program Files (x86)\Python311;%USERPROFILE%\AppData\Local\Programs\Python\Python311;%USERPROFILE%\AppData\Local\Programs\Python\Python312"

for %%p in (!SEARCH_PATHS!) do (
    if exist "%%p\python.exe" (
        echo ✅ Python gefunden: %%p\python.exe
        "%%p\python.exe" --version 2>nul
        if !PYTHON_FOUND! equ 0 (
            set "PYTHON_FOUND=1"
            set "WORKING_PYTHON=%%p\python.exe"
            set "MANUAL_PYTHON_PATH=%%p"
        )
    )
)

if !PYTHON_FOUND! equ 0 (
    echo ❌ Keine Python-Installation gefunden
)

echo.
echo 🔍 3. WARTUNGSMANAGER VIRTUAL ENVIRONMENT
echo ------------------------------------------
cd /d "C:\SoftwareProjekte\WartungsManager\Source\Python" 2>nul
if !errorlevel! equ 0 (
    echo Prüfe Virtual Environment...
    if exist "wartung_env\Scripts\python.exe" (
        echo ✅ Virtual Environment gefunden
        echo    Pfad: %CD%\wartung_env
        wartung_env\Scripts\python.exe --version 2>nul
        echo    Teste pip...
        wartung_env\Scripts\pip.exe --version >nul 2>&1
        if !errorlevel! equ 0 (
            echo ✅ pip im Virtual Environment funktioniert
        ) else (
            echo ❌ pip im Virtual Environment defekt
        )
    ) else (
        echo ❌ Virtual Environment fehlt oder beschädigt
    )
) else (
    echo ❌ Wartungsmanager-Projektverzeichnis nicht gefunden
)

echo.
echo 🔍 4. SYSTEM-PFAD ANALYSE
echo -------------------------
echo Aktuelle PATH-Variable analysieren...
echo %PATH% | findstr /i python >nul
if !errorlevel! equ 0 (
    echo ✅ Python-Pfade in PATH gefunden:
    echo %PATH% | findstr /i python
) else (
    echo ❌ Keine Python-Pfade in PATH-Variable
)

echo.
echo 🔍 5. REGISTRY-ANALYSE
echo ----------------------
echo Prüfe Python-Registrierung...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Python" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Python in System-Registry gefunden
    reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonCore" 2>nul | findstr /i "3.11\|3.12"
) else (
    echo ❌ Python nicht in System-Registry
)

reg query "HKEY_CURRENT_USER\SOFTWARE\Python" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Python in Benutzer-Registry gefunden
) else (
    echo ❌ Python nicht in Benutzer-Registry
)

echo.
echo 🔍 6. WARTUNGSMANAGER ANFORDERUNGEN PRÜFEN
echo -------------------------------------------
if exist "C:\SoftwareProjekte\WartungsManager\Source\Python\requirements.txt" (
    echo ✅ Requirements-Datei gefunden
    echo Analysiere Abhängigkeiten...
    type "C:\SoftwareProjekte\WartungsManager\Source\Python\requirements.txt" | findstr /v "^#" | findstr /v "^$" | wc -l 2>nul
    echo    Flask-Framework und SQLAlchemy erforderlich
) else (
    echo ❌ Requirements-Datei nicht gefunden
)

echo.
echo ========================================
echo 📋 DIAGNOSE-ZUSAMMENFASSUNG
echo ========================================

if !PYTHON_FOUND! equ 1 (
    echo ✅ PYTHON GEFUNDEN
    echo    Funktionsfähiger Python-Befehl: !WORKING_PYTHON!
    if defined PYTHON_VERSION echo    Version: !PYTHON_VERSION!
    if defined MANUAL_PYTHON_PATH echo    Installationspfad: !MANUAL_PYTHON_PATH!
    
    echo.
    echo 🔧 EMPFOHLENE REPARATUR-AKTIONEN:
    echo ================================
    
    if "!WORKING_PYTHON!"=="python" (
        echo ✅ Python-Befehl funktioniert bereits korrekt
        echo    Kein PATH-Problem vorhanden
    ) else (
        echo ⚠️  Python-PATH muss repariert werden
        echo    Python ist installiert, aber nicht im PATH
    )
    
    echo.
    echo 💡 NÄCHSTE SCHRITTE:
    echo ===================
    echo 1. Virtual Environment neu erstellen
    echo 2. Dependencies installieren  
    echo 3. Wartungsmanager starten
    echo.
    echo Möchten Sie die automatische Reparatur starten? (j/n)
    set /p repair_choice="Ihre Wahl: "
    
    if /i "!repair_choice!"=="j" (
        echo.
        echo 🔧 STARTE AUTOMATISCHE REPARATUR...
        echo ===================================
        call :repair_python
    )
    
) else (
    echo ❌ PYTHON NICHT GEFUNDEN
    echo.
    echo 🚨 KRITISCHES PROBLEM:
    echo ======================
    echo Python ist nicht installiert oder nicht funktionsfähig
    echo.
    echo 💡 LÖSUNGSOPTIONEN:
    echo ==================
    echo 1. Python 3.11.8 von python.org installieren
    echo 2. Wartungsmanager-Installer verwenden (setup_wartungsmanager.bat)
    echo 3. Python Portable manuell installieren
    echo.
    echo Möchten Sie Python automatisch installieren? (j/n)
    set /p install_choice="Ihre Wahl: "
    
    if /i "!install_choice!"=="j" (
        echo.
        echo 📥 INSTALLIERE PYTHON AUTOMATISCH...
        echo ===================================
        call :install_python
    )
)

echo.
echo ========================================
echo 📝 DIAGNOSE-LOG ERSTELLEN
echo ========================================
echo Erstelle detailliertes Log...

set "LOG_FILE=C:\SoftwareProjekte\WartungsManager\Logs\python_diagnose_%date:~10,4%-%date:~4,2%-%date:~7,2%_%time:~0,2%-%time:~3,2%.log"
if not exist "C:\SoftwareProjekte\WartungsManager\Logs" mkdir "C:\SoftwareProjekte\WartungsManager\Logs" >nul 2>&1

(
echo Python Diagnose Log - %date% %time%
echo =====================================
echo.
echo Python gefunden: !PYTHON_FOUND!
echo Funktionsfähiger Befehl: !WORKING_PYTHON!
echo Version: !PYTHON_VERSION!
echo Pfad: !PYTHON_PATH!
echo Manueller Pfad: !MANUAL_PYTHON_PATH!
echo.
echo System-PATH:
echo %PATH%
echo.
echo Registry-Status:
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Python" 2^>nul ^|^| echo NICHT_GEFUNDEN
echo.
echo Virtual Environment Status:
if exist "C:\SoftwareProjekte\WartungsManager\Source\Python\wartung_env\Scripts\python.exe" ^(
    echo GEFUNDEN
^) else ^(
    echo FEHLT
^)
) > "%LOG_FILE%" 2>&1

echo ✅ Log erstellt: %LOG_FILE%

echo.
echo Diagnose abgeschlossen!
echo Drücken Sie eine Taste zum Beenden...
pause >nul
exit /b 0

:repair_python
echo.
echo 🔧 PYTHON-REPARATUR GESTARTET
echo =============================

REM Zum Projektverzeichnis wechseln
cd /d "C:\SoftwareProjekte\WartungsManager\Source\Python" 2>nul
if !errorlevel! neq 0 (
    echo ❌ Projektverzeichnis nicht erreichbar
    goto repair_end
)

echo 1. Alte Virtual Environment löschen...
if exist "wartung_env" (
    echo    Lösche wartung_env...
    rmdir /s /q "wartung_env" >nul 2>&1
    echo ✅ Alte Virtual Environment entfernt
)

echo.
echo 2. Neue Virtual Environment erstellen...
"!WORKING_PYTHON!" -m venv wartung_env
if !errorlevel! equ 0 (
    echo ✅ Virtual Environment erfolgreich erstellt
) else (
    echo ❌ Virtual Environment-Erstellung fehlgeschlagen
    goto repair_end
)

echo.
echo 3. Virtual Environment aktivieren und Dependencies installieren...
call wartung_env\Scripts\activate.bat

if exist "requirements.txt" (
    echo    Installiere Requirements...
    wartung_env\Scripts\pip.exe install -r requirements.txt --quiet
    if !errorlevel! equ 0 (
        echo ✅ Dependencies erfolgreich installiert
    ) else (
        echo ⚠️  Einige Dependencies konnten nicht installiert werden
    )
) else (
    echo ❌ requirements.txt nicht gefunden
)

echo.
echo 4. Test: Wartungsmanager starten...
echo Teste Flask-Import...
wartung_env\Scripts\python.exe -c "import flask; print('Flask Version:', flask.__version__)"
if !errorlevel! equ 0 (
    echo ✅ Flask funktioniert korrekt
    echo.
    echo 🚀 REPARATUR ERFOLGREICH!
    echo =========================
    echo Sie können jetzt Wartungsmanager starten:
    echo 1. cd C:\SoftwareProjekte\WartungsManager\Source\Python
    echo 2. wartung_env\Scripts\activate.bat
    echo 3. python run.py
) else (
    echo ❌ Flask-Import fehlgeschlagen
)

:repair_end
echo.
echo Reparatur abgeschlossen.
return

:install_python
echo.
echo 📥 PYTHON-INSTALLATION GESTARTET
echo ================================

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

powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'" 2>nul

if exist "%PYTHON_INSTALLER%" (
    echo ✅ Download erfolgreich
    
    echo.
    echo 2. Installiere Python...
    echo    Stille Installation mit PATH-Integration...
    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    echo.
    echo 3. Installation abgeschlossen, teste...
    timeout /t 5 /nobreak >nul
    
    REM PATH neu laden
    call :refresh_environment
    
    python --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Python erfolgreich installiert!
        python --version
        set "PYTHON_FOUND=1"
        set "WORKING_PYTHON=python"
        
        echo.
        echo Möchten Sie jetzt die Virtual Environment einrichten? (j/n)
        set /p setup_venv="Ihre Wahl: "
        if /i "!setup_venv!"=="j" call :repair_python
    ) else (
        echo ❌ Python-Installation fehlgeschlagen
        echo Bitte Python manuell von python.org installieren
    )
    
    REM Installer löschen
    del "%PYTHON_INSTALLER%" >nul 2>&1
) else (
    echo ❌ Download fehlgeschlagen
    echo Bitte Python manuell von python.org installieren
)

return

:refresh_environment
REM Aktualisiert die Umgebungsvariablen ohne Neustart
for /f "tokens=2*" %%a in ('reg query "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH') do set "SYSTEM_PATH=%%b"
for /f "tokens=2*" %%a in ('reg query "HKEY_CURRENT_USER\Environment" /v PATH 2^>nul') do set "USER_PATH=%%b"
set "PATH=%SYSTEM_PATH%;%USER_PATH%"
return
