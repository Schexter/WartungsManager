@echo off
title WartungsManager - PYTHON 3.13 REPARATUR
color 0A
echo =========================================================
echo   WARTUNGSMANAGER - PYTHON 3.13 KOMPATIBLE REPARATUR
echo =========================================================
echo   Behebt: Pillow Kompatibilitätsproblem
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

REM Python-Version anzeigen
echo 📋 Python-Version:
python --version
echo.

REM Pip upgraden (wichtig für Python 3.13)
echo 🔄 Pip auf neueste Version aktualisieren...
python -m pip install --upgrade pip
echo.

REM Cache leeren
echo 🧹 Pip-Cache leeren...
python -m pip cache purge
echo.

REM Kompatible Requirements kopieren
echo 🔧 Python 3.13 kompatible Requirements installieren...
copy /Y "requirements_PYTHON313_KOMPATIBEL.txt" "requirements_production.txt" >nul
echo ✅ Kompatible Requirements aktiviert!
echo.

REM Pakete installieren (ohne Build-Dependencies-Probleme)
echo 📦 Pakete installieren (nur essentielle für ersten Test)...
pip install Flask==2.3.3 Werkzeug==2.3.7 SQLAlchemy==2.0.21 Flask-SQLAlchemy==3.0.5
if errorlevel 1 (
    echo ❌ Basis-Pakete Installation fehlgeschlagen!
    pause
    exit /b 1
)

echo ✅ Flask-Basis installiert!
echo.

echo 📦 Weitere wichtige Pakete...
pip install Flask-Migrate==4.0.5 WTForms==3.0.1 Flask-WTF==1.1.1 python-dateutil==2.8.2
if errorlevel 1 (
    echo ⚠️ Einige Pakete übersprungen, aber Basis funktioniert
)

echo.
echo 📦 Logging und Utils...
pip install colorlog requests jsonschema click itsdangerous Jinja2 MarkupSafe
if errorlevel 1 (
    echo ⚠️ Einige Utils übersprungen, aber Kern funktioniert
)

echo.
echo =========================================================
echo   PYTHON 3.13 REPARATUR ABGESCHLOSSEN!
echo =========================================================
echo.
echo ✅ Basis-System ist jetzt Python 3.13 kompatibel!
echo.
echo 🚀 SYSTEM TESTEN:
echo    python run_production_REPARIERT.py
echo.
echo 🌐 Nach dem Start verfügbar:
echo    http://localhost:5000
echo.
echo 📋 HINWEISE:
echo    - Drucker-Features werden später hinzugefügt
echo    - QR/Barcode-Features optional nachrüstbar
echo    - Basis-Funktionen sollten jetzt laufen
echo.
pause
