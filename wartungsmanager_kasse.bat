@echo off
title Wartungsmanager Kasse - Client Startup
color 0B

REM NAS-Server Konfiguration (ANPASSEN!)
set NAS_IP=192.168.1.100
set NAS_PORT=5000
set WARTUNGSMANAGER_URL=http://%NAS_IP%:%NAS_PORT%

echo ========================================
echo    WARTUNGSMANAGER - KASSENSYSTEM
echo ========================================
echo.
echo 🌐 Verbinde zu NAS-Server...
echo 📍 Server: %WARTUNGSMANAGER_URL%
echo.

REM Server-Erreichbarkeit prüfen (optional)
echo Prüfe Server-Verfügbarkeit...
ping -n 1 %NAS_IP% >nul 2>&1
if errorlevel 1 (
    echo ⚠️  WARNING: NAS nicht erreichbar (%NAS_IP%)
    echo Versuche trotzdem Browser zu starten...
    timeout /t 2 /nobreak >nul
) else (
    echo ✅ NAS ist erreichbar
)

echo.
echo 🚀 Starte Browser im Kiosk-Modus...

REM Browser-Erkennung und Start (Priorität: Chrome > Edge > Firefox > Default)
set BROWSER_STARTED=0

REM Google Chrome (Kiosk-Modus - ideal für Kasse)
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo 🌐 Starte Google Chrome im Vollbild-Modus...
    start "Wartungsmanager-Kasse" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
        --new-window ^
        --disable-infobars ^
        --disable-extensions ^
        --disable-dev-tools ^
        --no-first-run ^
        --fast ^
        --fast-start ^
        --disable-default-apps ^
        --window-size=1920,1080 ^
        --start-maximized ^
        "%WARTUNGSMANAGER_URL%"
    set BROWSER_STARTED=1
    goto browser_success
)

REM Google Chrome (x86)
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo 🌐 Starte Google Chrome (x86) im Vollbild-Modus...
    start "Wartungsmanager-Kasse" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" ^
        --new-window ^
        --start-maximized ^
        "%WARTUNGSMANAGER_URL%"
    set BROWSER_STARTED=1
    goto browser_success
)

REM Microsoft Edge (Chromium)
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    echo 🌐 Starte Microsoft Edge im Vollbild-Modus...
    start "Wartungsmanager-Kasse" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" ^
        --new-window ^
        --start-maximized ^
        "%WARTUNGSMANAGER_URL%"
    set BROWSER_STARTED=1
    goto browser_success
)

REM Firefox
if exist "C:\Program Files\Mozilla Firefox\firefox.exe" (
    echo 🌐 Starte Firefox...
    start "Wartungsmanager-Kasse" "C:\Program Files\Mozilla Firefox\firefox.exe" -new-window "%WARTUNGSMANAGER_URL%"
    set BROWSER_STARTED=1
    goto browser_success
)

REM Standard-Browser als Fallback
if %BROWSER_STARTED%==0 (
    echo 🌐 Starte Standard-Browser...
    start "Wartungsmanager-Kasse" "%WARTUNGSMANAGER_URL%"
    set BROWSER_STARTED=1
)

:browser_success
if %BROWSER_STARTED%==1 (
    echo ✅ Browser erfolgreich gestartet
    echo.
    echo ========================================
    echo   WARTUNGSMANAGER BEREIT
    echo ========================================
    echo 📍 URL: %WARTUNGSMANAGER_URL%
    echo 💻 Bedienung: Touch-optimiert für Kassensystem
    echo 📱 iPad-Modus: Automatisch aktiviert bei Touch-Geräten
    echo.
    echo ℹ️  Dieses Fenster kann geschlossen werden
    echo 🔄 Browser neu starten: Nochmal diese Datei ausführen
    echo.
    
    REM Warte kurz und schließe automatisch (optional)
    echo Browser wird gestartet... Fenster schließt automatisch in 5 Sekunden
    timeout /t 5 /nobreak >nul
    exit
) else (
    echo ❌ FEHLER: Kein Browser gefunden!
    echo.
    echo Bitte installieren Sie einen der folgenden Browser:
    echo - Google Chrome (empfohlen)
    echo - Microsoft Edge
    echo - Mozilla Firefox
    echo.
    echo Oder öffnen Sie manuell: %WARTUNGSMANAGER_URL%
    pause
    exit /b 1
)
