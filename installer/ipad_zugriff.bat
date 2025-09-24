@echo off
title iPad Zugriff - Wartungsmanager
color 0B

echo ========================================
echo   IPAD-ZUGRIFF KONFIGURATION
echo ========================================
echo.

REM Kassenrechner-IP automatisch ermitteln
echo 📡 Ermittle Kassenrechner-IP...
set LOCAL_IP=192.168.0.209
echo ✅ Kassenrechner-IP: %LOCAL_IP% (Konfiguriert)

echo.
echo ========================================
echo   IPAD-ZUGRIFF ANLEITUNG
echo ========================================
echo.
echo 📱 Für iPad-Zugriff verwenden Sie:
echo.
echo    🌐 URL: http://%LOCAL_IP%:5000
echo.
echo 📋 Anleitung für iPad:
echo    1. Safari öffnen
echo    2. URL eingeben: http://%LOCAL_IP%:5000
echo    3. "Zum Home-Bildschirm hinzufügen" für App-Zugriff
echo    4. iPad-Modus wird automatisch erkannt
echo.
echo ✅ iPad-Features automatisch aktiviert:
echo    - Popup-freie Bedienung
echo    - Touch-optimierte Buttons (44px+)
echo    - Inline-Formulare statt Modals
echo    - Toast-Benachrichtigungen statt Alerts
echo.

REM QR-Code-URL für einfachen iPad-Zugriff erstellen
echo 📱 QR-Code-URL für iPad:
echo    https://api.qrserver.com/v1/create-qr-code/?size=200x200^&data=http://%LOCAL_IP%:5000
echo.

REM IP in Zwischenablage kopieren (optional)
echo 📋 IP-Adresse in Zwischenablage kopieren?
choice /c JN /n /m "[J]a oder [N]ein: "
if errorlevel 1 (
    echo %LOCAL_IP%:5000 | clip
    echo ✅ IP:Port in Zwischenablage kopiert
)

echo.
echo ========================================
echo   NETZWERK-TEST
echo ========================================
echo.
echo 🔍 Teste Wartungsmanager-Erreichbarkeit...

REM Server-Test
curl -s http://%LOCAL_IP%:5000 >nul 2>&1
if %errorlevel% EQU 0 (
    echo ✅ Wartungsmanager ist erreichbar
    echo 🌐 Server läuft auf: http://%LOCAL_IP%:5000
) else (
    echo ❌ Wartungsmanager nicht erreichbar
    echo.
    echo 🔧 Mögliche Lösungen:
    echo    - Wartungsmanager starten: Doppelklick Desktop-Icon
    echo    - Firewall prüfen: Windows Defender Firewall
    echo    - Port prüfen: netstat -an ^| findstr :5000
)

echo.
echo ========================================
echo   WEITERE GERÄTE
echo ========================================
echo.
echo 🖥️  Andere PCs im Netzwerk:
echo    URL: http://%LOCAL_IP%:5000
echo.
echo 📱 Smartphones/Tablets:
echo    URL: http://%LOCAL_IP%:5000
echo    Touch-optimiert: Automatisch erkannt
echo.
echo 💻 Weitere Kassenrechner:
echo    URL: http://%LOCAL_IP%:5000
echo    Vollbild-Modus: F11 in Browser
echo.

echo Drücken Sie eine Taste zum Beenden...
pause >nul
