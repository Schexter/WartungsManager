@echo off
title WD My Cloud NAS - Wartungsmanager Setup
color 0C

echo ========================================
echo   WD MY CLOUD NAS DEPLOYMENT
echo ========================================
echo   NAS-IP: 192.168.0.231
echo   Pfad: \\192.168.0.231\Tauchen\KompressorUeberwachung
echo ========================================
echo.

REM NAS-Verbindung testen
echo 📡 Teste NAS-Verbindung...
ping -n 1 192.168.0.231 >nul 2>&1
if %errorlevel% NEQ 0 (
    echo ❌ FEHLER: WD My Cloud nicht erreichbar!
    echo.
    echo Prüfen Sie:
    echo - NAS ist eingeschaltet und betriebsbereit
    echo - Netzwerk-Verbindung funktioniert
    echo - IP-Adresse 192.168.0.231 ist korrekt
    echo.
    pause
    exit /b 1
)
echo ✅ WD My Cloud erreichbar

REM NAS-Pfad prüfen
echo 📁 Prüfe NAS-Pfad...
if not exist "\\192.168.0.231\Tauchen" (
    echo ❌ FEHLER: Ordner 'Tauchen' nicht gefunden auf NAS
    echo.
    echo Bitte erstellen Sie den Ordner-Pfad:
    echo \\192.168.0.231\Tauchen\KompressorUeberwachung
    echo.
    pause
    exit /b 1
)

REM Zielordner erstellen falls nicht vorhanden
set NAS_PATH=\\192.168.0.231\Tauchen\KompressorUeberwachung
if not exist "%NAS_PATH%" (
    echo 📁 Erstelle Zielordner auf NAS...
    mkdir "%NAS_PATH%" 2>nul
    if %errorlevel% NEQ 0 (
        echo ❌ FEHLER: Kann Ordner auf NAS nicht erstellen
        echo Berechtigung prüfen oder manuell erstellen
        pause
        exit /b 1
    )
)
echo ✅ NAS-Pfad verfügbar: %NAS_PATH%

echo.
echo ========================================
echo   WARTUNGSMANAGER AUF NAS KOPIEREN
echo ========================================

echo 📂 Kopiere Wartungsmanager-Dateien zur NAS...

REM Source-Verzeichnis bestimmen
set SOURCE_DIR=%~dp0..\Source\Python
if not exist "%SOURCE_DIR%" (
    echo ❌ FEHLER: Source-Verzeichnis nicht gefunden
    echo Bitte Installer im Wartungsmanager-Hauptverzeichnis ausführen
    pause
    exit /b 1
)

echo    Quelle: %SOURCE_DIR%
echo    Ziel: %NAS_PATH%

REM Dateien kopieren
xcopy "%SOURCE_DIR%\*" "%NAS_PATH%\" /E /I /Y /Q
if %errorlevel% EQU 0 (
    echo ✅ Wartungsmanager-Dateien erfolgreich zur NAS kopiert
) else (
    echo ❌ FEHLER beim Kopieren zur NAS
    pause
    exit /b 1
)

echo.
echo ========================================
echo   NAS-SPEZIFISCHE KONFIGURATION
echo ========================================

echo 🔧 Erstelle NAS-Konfiguration...

REM Produktions-Konfiguration für NAS erstellen
(
echo # WD My Cloud NAS Konfiguration - Automatisch generiert
echo import os
echo.
echo class NASConfig:
echo     HOST = '0.0.0.0'  # Alle Netzwerk-Interfaces
echo     PORT = 5000
echo     DEBUG = False
echo     
echo     # SQLite für NAS optimiert
echo     SQLALCHEMY_DATABASE_URI = 'sqlite:///database/wartungsmanager.db'
echo     SQLALCHEMY_ENGINE_OPTIONS = {
echo         'pool_pre_ping': True,
echo         'pool_recycle': 300,
echo         'connect_args': {
echo             'check_same_thread': False,  # Multi-Client Support
echo             'timeout': 10
echo         }
echo     }
echo     
echo     SECRET_KEY = 'Magicfactory15!_NAS_PRODUCTION_2025'
echo     
echo     # NAS-spezifische Einstellungen
echo     ALLOW_MULTIPLE_CLIENTS = True
echo     MAX_CONCURRENT_CLIENTS = 10
echo     ENABLE_TOUCH_OPTIMIZATION = True
echo     IPAD_MODE_AUTO_DETECT = True
) > "%NAS_PATH%\config\nas.py"

echo ✅ NAS-Konfiguration erstellt

echo.
echo ========================================
echo   NAS AUTO-START SCRIPT
echo ========================================

echo 🚀 Erstelle NAS Auto-Start Script...

REM Start-Script für NAS angepasst
(
echo @echo off
echo title Wartungsmanager Server - WD My Cloud NAS
echo color 0A
echo.
echo echo ========================================
echo echo   WARTUNGSMANAGER NAS SERVER
echo echo ========================================
echo echo NAS: 192.168.0.231:5000
echo echo Pfad: \\192.168.0.231\Tauchen\KompressorUeberwachung
echo echo ========================================
echo echo.
echo.
echo cd /d "\\192.168.0.231\Tauchen\KompressorUeberwachung"
echo if errorlevel 1 ^(
echo     echo ❌ FEHLER: NAS-Pfad nicht erreichbar!
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo ✅ NAS-Pfad erreichbar: %%CD%%
echo echo.
echo.
echo REM Python-Pfad ermitteln
echo set PYTHON_PATH=python
echo python --version ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     echo ❌ FEHLER: Python nicht installiert auf NAS!
echo     echo Bitte Python auf der NAS installieren
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo ✅ Python verfügbar
echo echo.
echo.
echo REM Dependencies installieren
echo echo 📦 Installiere Dependencies...
echo pip install -r requirements.txt --quiet 2^>nul
echo.
echo REM Datenbank Setup
echo echo 💾 Initialisiere Datenbank...
echo if not exist "database" mkdir database
echo if not exist "logs" mkdir logs
echo.
echo REM Server starten
echo echo ========================================
echo echo   SERVER STARTUP
echo echo ========================================
echo echo.
echo echo 🌐 Server startet auf: http://192.168.0.231:5000
echo echo.
echo echo Zugriff von Clients:
echo echo 💻 Kasse: http://192.168.0.231:5000
echo echo 📱 iPad: http://192.168.0.231:5000
echo echo 🌐 Browser: http://192.168.0.231:5000
echo echo.
echo echo ⏹️  CTRL+C zum Beenden
echo echo ========================================
echo echo.
echo.
echo python run.py
echo.
echo echo Server beendet.
echo pause
) > "%NAS_PATH%\start_nas_server.bat"

echo ✅ NAS Auto-Start Script erstellt

echo.
echo ========================================
echo   CLIENT-ZUGRIFF SCRIPTS
echo ========================================

echo 🖥️ Erstelle Client-Zugriff Scripts...

REM Kassen-Client für NAS-Server
(
echo @echo off
echo title Wartungsmanager - Client ^(NAS-Server^)
echo color 0B
echo.
echo echo Wartungsmanager Client
echo echo ======================
echo echo Server: WD My Cloud NAS ^(192.168.0.231:5000^)
echo echo.
echo.
echo echo 📡 Prüfe NAS-Server...
echo ping -n 1 192.168.0.231 ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     echo ❌ NAS nicht erreichbar!
echo     echo Bitte NAS-Server starten
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo ✅ NAS erreichbar - starte Browser...
echo echo.
echo.
echo REM Browser-Start mit NAS-URL
echo set NAS_URL=http://192.168.0.231:5000
echo.
echo if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" ^(
echo     start "Wartungsmanager" "C:\Program Files\Google\Chrome\Application\chrome.exe" --new-window --start-maximized "%%NAS_URL%%"
echo ^) else if exist "C:\Program Files ^(x86^)\Microsoft\Edge\Application\msedge.exe" ^(
echo     start "Wartungsmanager" "C:\Program Files ^(x86^)\Microsoft\Edge\Application\msedge.exe" --new-window --start-maximized "%%NAS_URL%%"
echo ^) else ^(
echo     start "Wartungsmanager" "%%NAS_URL%%"
echo ^)
echo.
echo echo Browser gestartet - Wartungsmanager sollte laden...
echo timeout /t 3 /nobreak ^>nul
echo exit
) > "%NAS_PATH%\kasse_client.bat"

REM Desktop-Shortcut für Kassen-PCs
(
echo [InternetShortcut]
echo URL=http://192.168.0.231:5000
echo IconFile=C:\Windows\System32\shell32.dll
echo IconIndex=14
) > "%NAS_PATH%\Wartungsmanager_NAS.url"

echo ✅ Client-Zugriff Scripts erstellt

echo.
echo ========================================
echo   INSTALLATION ABGESCHLOSSEN
echo ========================================
echo.
echo ✅ Wartungsmanager erfolgreich auf WD My Cloud installiert!
echo.
echo 📍 NAS-Pfad: %NAS_PATH%
echo 🌐 Server-URL: http://192.168.0.231:5000
echo.
echo ========================================
echo   NÄCHSTE SCHRITTE:
echo ========================================
echo.
echo 🔧 Auf der NAS:
echo    1. Python installieren (falls nicht vorhanden)
echo    2. start_nas_server.bat ausführen
echo    3. Server läuft dann 24/7
echo.
echo 💻 Auf Kassen-PCs:
echo    1. kasse_client.bat auf Desktop kopieren
echo    2. Oder Wartungsmanager_NAS.url verwenden
echo    3. Doppelklick öffnet Browser automatisch
echo.
echo 📱 Für iPad:
echo    1. Safari öffnen
echo    2. http://192.168.0.231:5000 eingeben
echo    3. "Zum Home-Bildschirm hinzufügen"
echo.

echo Möchten Sie die Client-Dateien jetzt auf den Desktop kopieren?
choice /c JN /n /m "[J]a oder [N]ein: "
if errorlevel 1 (
    echo.
    echo 📂 Kopiere Client-Dateien auf Desktop...
    copy "%NAS_PATH%\kasse_client.bat" "%USERPROFILE%\Desktop\Wartungsmanager ^(NAS^).bat" >nul
    copy "%NAS_PATH%\Wartungsmanager_NAS.url" "%USERPROFILE%\Desktop\" >nul
    echo ✅ Client-Dateien auf Desktop kopiert
)

echo.
echo ========================================
echo Installation completed!
echo.
echo 🚀 Starten Sie jetzt "start_nas_server.bat" auf der NAS
echo 💻 Verwenden Sie "Wartungsmanager (NAS).bat" auf Clients
echo.
pause
