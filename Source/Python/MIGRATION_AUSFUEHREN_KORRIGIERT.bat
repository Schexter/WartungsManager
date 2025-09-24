@echo off
echo 🚀 WartungsManager - Erweiterte Flaschen-Rueckverfolgbarkeit Migration
echo ================================================================
echo.

cd /d "C:\SoftwareProjekte\WartungsManager\Source\Python"

echo 📂 Aktuelles Verzeichnis: %CD%
echo.

echo 🔧 Starte korrigierte Migration...
python migration_flaschen_KORRIGIERT.py

echo.
echo ⏸️ Druecken Sie eine beliebige Taste um fortzufahren...
pause > nul
