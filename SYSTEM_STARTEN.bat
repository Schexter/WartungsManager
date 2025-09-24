@echo off
title WartungsManager - SYSTEM STARTEN
color 0A
echo =========================================================
echo   WARTUNGSMANAGER - SYSTEM STARTEN
echo =========================================================
echo.

cd /d "C:\SoftwareEntwicklung\WartungsManager-main"

echo 📁 Arbeitsverzeichnis: %CD%
echo 🐍 Python-Version:
python --version
echo.

echo 🚀 Starte WartungsManager...
echo 📱 Nach dem Start verfügbar: http://localhost:5000
echo ⏹️  CTRL+C zum Beenden
echo.
echo =========================================================

REM Versuche zuerst die reparierte Version
echo 🔧 Versuche: run_production_REPARIERT.py
python run_production_REPARIERT.py
if errorlevel 1 (
    echo.
    echo ⚠️ Fallback: Versuche minimale Version...
    python run_MINIMAL_PYTHON313.py
)

pause
