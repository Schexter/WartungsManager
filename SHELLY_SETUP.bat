@echo off
REM ============================================================
REM WartungsManager - Shelly Auto-Discovery Setup
REM ============================================================

echo.
echo ============================================================
echo      WartungsManager - Shelly Smart Home Setup
echo ============================================================
echo.

cd /d "C:\SoftwareEntwicklung\WartungsManager-main\Source\Python"

echo [1/3] Pruefe Python-Installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo FEHLER: Python nicht gefunden!
    echo Bitte installieren Sie Python 3.13 oder hoeher
    pause
    exit /b 1
)

echo [2/3] Installiere benoetigte Pakete...
pip install python-dotenv requests --quiet

echo [3/3] Starte Shelly Discovery...
echo.
echo ============================================================
echo.
echo WICHTIG: Stellen Sie sicher dass:
echo   - Alle Shellys eingeschaltet sind
echo   - Shellys im gleichen WLAN wie dieser PC sind
echo   - Windows Firewall ggf. deaktiviert ist
echo.
echo ============================================================
echo.

timeout /t 3 >nul

python shelly_discovery.py

echo.
echo ============================================================
echo      Setup abgeschlossen!
echo ============================================================
echo.
echo Dashboard erreichbar unter:
echo   http://localhost:5000/shelly/dashboard
echo.
echo Server starten mit:
echo   python run_production.py
echo.

pause
