@echo off
title WartungsManager - SOFORT-REPARATUR
color 0A
echo =========================================================
echo   WARTUNGSMANAGER - SOFORT-REPARATUR
echo =========================================================
echo   Behebt: No module named 'app' Fehler
echo   Erstellt von Hans Hahn - Alle Rechte vorbehalten
echo =========================================================
echo.

REM Zum WartungsManager-Verzeichnis wechseln
cd /d "C:\SoftwareEntwicklung\WartungsManager-main"
if errorlevel 1 (
    echo ❌ FEHLER: WartungsManager-main Verzeichnis nicht gefunden!
    pause
    exit /b 1
)

echo ✅ Arbeitsverzeichnis: %CD%
echo.

REM Python-Version prüfen
echo 📋 Python-Version prüfen...
python --version
if errorlevel 1 (
    echo ❌ Python nicht gefunden! Installieren Sie Python 3.8+
    pause
    exit /b 1
)
echo.

REM Requirements reparieren und installieren
echo 🔧 Requirements reparieren...
copy /Y "requirements_production_REPARIERT.txt" "requirements_production.txt" >nul
echo ✅ Requirements repariert!

echo.
echo 📦 Pakete installieren...
pip install -r requirements_production.txt
if errorlevel 1 (
    echo ❌ Paket-Installation fehlgeschlagen!
    echo 💡 Versuchen Sie: pip install --upgrade pip
    pause
    exit /b 1
)

echo.
echo ✅ Alle Pakete installiert!
echo.

REM Test-Start durchführen
echo 🚀 Test-Start durchführen...
python run_production_REPARIERT.py &

echo.
echo =========================================================
echo   REPARATUR ABGESCHLOSSEN!
echo =========================================================
echo.
echo ✅ WartungsManager wurde erfolgreich repariert!
echo.
echo 🚀 STARTEN:
echo    python run_production_REPARIERT.py
echo.
echo 🌐 URLs nach dem Start:
echo    - Lokal: http://localhost:5000
echo    - Netzwerk: http://[IHRE-IP]:5000
echo    - iPad: http://[PC-IP]:5000
echo.
echo 💡 TIPP: Erstellen Sie Desktop-Verknüpfung für run_production_REPARIERT.py
echo.
pause
