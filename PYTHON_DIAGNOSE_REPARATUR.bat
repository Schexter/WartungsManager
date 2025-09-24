@echo off
setlocal enabledelayedexpansion
echo ========================================
echo 🐍 PYTHON DIAGNOSE UND REPARATUR
echo ========================================
echo.

echo 📊 SYSTEM ANALYSE...
echo =====================================

echo.
echo 🔍 1. PYTHON-INSTALLATIONEN ERKENNEN
echo -------------------------------------
echo Suche nach Python-Installationen...

where python >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ 'python' Befehl erkannt
    python --version
) else (
    echo ❌ 'python' Befehl NICHT erkannt
)

where py >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ 'py' Launcher erkannt
    py --version
    echo.
    echo Verfügbare Python-Versionen:
    py -0
) else (
    echo ❌ 'py' Launcher NICHT erkannt
)

echo.
echo 🔍 2. REGISTRY-PRÜFUNG
echo ------------------------
echo Suche Python in Registry...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Python" /s >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Python in Registry gefunden
    reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonCore" 2>nul
) else (
    echo ❌ Python NICHT in Registry
)

echo.
echo 🔍 3. PFAD-ANALYSE
echo ------------------
echo Aktuelle PATH-Variable:
echo %PATH% | findstr /i python
if !errorlevel! equ 0 (
    echo ✅ Python-Pfade in PATH gefunden
) else (
    echo ❌ Keine Python-Pfade in PATH
)

echo.
echo 🔍 4. MANUELLE INSTALLATION SUCHEN
echo ----------------------------------
if exist "C:\Python311\python.exe" (
    echo ✅ Python 3.11 gefunden: C:\Python311\python.exe
    "C:\Python311\python.exe" --version
    set "MANUAL_PYTHON_PATH=C:\Python311"
) else (
    echo ❌ Python 3.11 nicht in C:\Python311
)

if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe" (
    echo ✅ Python 3.11 (Benutzer) gefunden: %USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe
    "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe" --version
    set "MANUAL_PYTHON_PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python311"
) else (
    echo ❌ Python 3.11 nicht im Benutzerpfad
)

echo.
echo 🔍 5. VIRTUAL ENVIRONMENT PRÜFUNG
echo ----------------------------------
cd /d "C:\SoftwareProjekte\WartungsManager\Source\Python"
if exist "wartung_env\Scripts\python.exe" (
    echo ✅ Virtual Environment gefunden
    wartung_env\Scripts\python.exe --version
) else (
    echo ❌ Virtual Environment fehlt oder beschädigt
)

echo.
echo ========================================
echo 🔧 REPARATUR-OPTIONEN
echo ========================================

if defined MANUAL_PYTHON_PATH (
    echo.
    echo Option 1: PFAD REPARIEREN
    echo ========================
    echo Python ist installiert aber nicht im PATH!
    echo.
    echo Möchten Sie den PATH automatisch reparieren? (j/n^)
    set /p repair_path="Ihre Wahl: "
    
    if /i "!repair_path!"=="j" (
        echo.
        echo 🔧 Repariere PATH...
        setx PATH "%PATH%;!MANUAL_PYTHON_PATH!;!MANUAL_PYTHON_PATH!\Scripts"
        echo ✅ PATH repariert! Bitte PowerShell/CMD neu öffnen.
        echo.
        goto venv_repair
    )
)

echo.
echo Option 2: VIRTUAL ENVIRONMENT REPARIEREN
echo =========================================
:venv_repair
if defined MANUAL_PYTHON_PATH (
    echo Verwende gefundene Python-Installation: !MANUAL_PYTHON_PATH!
    set "PYTHON_EXE=!MANUAL_PYTHON_PATH!\python.exe"
) else (
    echo Verwende Standard Python-Befehl...
    set "PYTHON_EXE=python"
)

echo.
echo Möchten Sie das Virtual Environment neu erstellen? (j/n^)
set /p repair_venv="Ihre Wahl: "

if /i "!repair_venv!"=="j" (
    echo.
    echo 🔧 Repariere Virtual Environment...
    
    if exist "wartung_env" (
        echo Lösche altes Virtual Environment...
        rmdir /s /q wartung_env
    )
    
    echo Erstelle neues Virtual Environment...
    "!PYTHON_EXE!" -m venv wartung_env
    
    if exist "wartung_env\Scripts\activate.bat" (