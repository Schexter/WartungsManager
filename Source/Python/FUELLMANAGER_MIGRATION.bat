@echo off
echo =======================================
echo Fuellmanager Migration
echo =======================================
echo.

cd /d %~dp0

echo Aktiviere Python-Umgebung...
call wartung_env\Scripts\activate.bat

echo.
echo Starte Migration...
python migration_fuellmanager.py

echo.
echo =======================================
echo Migration abgeschlossen!
echo =======================================
echo.

pause
