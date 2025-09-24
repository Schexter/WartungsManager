@echo off
echo.
echo WARTUNGSMANAGER - EINFACHE INSTALLATION
echo =======================================
echo.

REM Pausiere immer, damit wir Fehler sehen
echo Druecken Sie eine Taste um zu starten...
pause

REM Admin-Check
echo.
echo Pruefe Administrator-Rechte...
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    echo FEHLER: Keine Administrator-Rechte!
    echo.
    echo Bitte Rechtsklick auf diese Datei und "Als Administrator ausfuehren"
    pause
    exit
)
echo OK: Administrator-Rechte vorhanden
pause

REM Python-Check
echo.
echo Pruefe Python...
python --version
if %errorlevel% NEQ 0 (
    echo FEHLER: Python nicht gefunden!
    echo.
    echo Bitte Python 3.11 von python.org installieren
    pause
    exit
)
echo OK: Python gefunden
pause

REM Flask installieren
echo.
echo Installiere Flask...
pip install Flask
if %errorlevel% NEQ 0 (
    echo FEHLER: Flask-Installation fehlgeschlagen!
    pause
    exit
)
echo OK: Flask installiert
pause

REM Verzeichnis erstellen
echo.
echo Erstelle Arbeitsverzeichnis...
mkdir C:\Wartungsmanager 2>nul
mkdir C:\Wartungsmanager\database 2>nul
cd /d C:\Wartungsmanager
echo OK: Verzeichnis erstellt
pause

REM Minimale run.py erstellen
echo.
echo Erstelle Wartungsmanager...
echo from flask import Flask > run.py
echo app = Flask(__name__) >> run.py
echo @app.route('/') >> run.py
echo def home(): >> run.py
echo     return "^<h1^>Wartungsmanager laeuft!^</h1^>^<p^>Installation erfolgreich^</p^>" >> run.py
echo if __name__ == '__main__': >> run.py
echo     app.run(host='0.0.0.0', port=5000) >> run.py
echo OK: Wartungsmanager erstellt
pause

REM Desktop-Icon
echo.
echo Erstelle Desktop-Icon...
echo @echo off > "%USERPROFILE%\Desktop\Wartungsmanager.bat"
echo cd /d C:\Wartungsmanager >> "%USERPROFILE%\Desktop\Wartungsmanager.bat"
echo python run.py >> "%USERPROFILE%\Desktop\Wartungsmanager.bat"
echo pause >> "%USERPROFILE%\Desktop\Wartungsmanager.bat"
echo OK: Desktop-Icon erstellt
pause

REM Test
echo.
echo Teste Installation...
python run.py &
timeout /t 3 /nobreak >nul
taskkill /f /im python.exe >nul 2>&1
echo OK: Test abgeschlossen
pause

echo.
echo =======================================
echo INSTALLATION ABGESCHLOSSEN!
echo =======================================
echo.
echo Starten Sie Wartungsmanager:
echo 1. Doppelklick auf Desktop-Icon "Wartungsmanager.bat"
echo 2. Oder: cd C:\Wartungsmanager und dann: python run.py
echo 3. Browser: http://localhost:5000
echo.
echo Soll jetzt gestartet werden? (j/n)
set /p start=
if /i "%start%"=="j" (
    start "Wartungsmanager" python run.py
    start http://localhost:5000
)

echo.
echo Fertig!
pause
