@echo off
title Wartungsmanager - Installation Auswahl
color 0F
mode con: cols=90 lines=35

echo.
echo ████████████████████████████████████████████████████████████████████████████████████
echo ██                                                                                ██
echo ██    ██     ██  █████  ██████  ████████ ██    ██ ███    ██  ██████  ███████     ██
echo ██    ██     ██ ██   ██ ██   ██    ██    ██    ██ ████   ██ ██       ██          ██
echo ██    ██  █  ██ ███████ ██████     ██    ██    ██ ██ ██  ██ ██   ███ ███████     ██
echo ██    ██ ███ ██ ██   ██ ██   ██    ██    ██    ██ ██  ██ ██ ██    ██      ██     ██
echo ██     ███ ███  ██   ██ ██   ██    ██     ██████  ██   ████  ██████  ███████     ██
echo ██                                                                                ██
echo ██                        MANAGER - INSTALLER v1.0                              ██
echo ██                                                                                ██
echo ████████████████████████████████████████████████████████████████████████████████████
echo.
echo                           Vollautomatische Installation
echo                              für Kompressor-Überwachung
echo.
echo ================================================================================
echo   INSTALLATIONS-OPTIONEN
echo ================================================================================
echo.
echo   Sie haben zwei Möglichkeiten für die Installation:
echo.
echo   [1] KASSENRECHNER als Server (EMPFOHLEN)
echo       ✅ Beste Performance und Zuverlässigkeit
echo       ✅ Vollautomatische Installation mit 1-Klick
echo       ✅ Desktop-Icon und Auto-Start
echo       ✅ NAS-Backup zur WD My Cloud automatisch
echo       ✅ iPad/Touch-optimiert mit popup-freier Bedienung
echo.
echo   [2] WD MY CLOUD NAS als Server
echo       ✅ Zentrale Datenhaltung auf NAS
echo       ✅ 24/7 Verfügbarkeit (falls NAS immer läuft)
echo       ✅ Mehrere Clients können gleichzeitig zugreifen
echo       ⚠️  Benötigt Python-Installation auf NAS
echo.
echo ================================================================================
echo   SYSTEM-INFORMATIONEN
echo ================================================================================
echo.
echo   🌐 WD My Cloud NAS:     192.168.0.231
echo   📁 NAS-Pfad:            \\192.168.0.231\Tauchen\KompressorUeberwachung
echo   💻 Kassenrechner:       192.168.0.209 (dieser PC - lokale Installation)
echo   📱 iPad-Unterstützung:  Beide Optionen popup-frei und touch-optimiert
echo.
echo ================================================================================

:menu
echo.
echo   Welche Installation möchten Sie durchführen?
echo.
echo   [1] Kassenrechner-Installation (empfohlen)
echo   [2] WD My Cloud NAS-Installation  
echo   [3] Hilfe und weitere Informationen
echo   [4] Beenden
echo.
choice /c 1234 /n /m "   Ihre Auswahl (1-4): "

if errorlevel 4 goto exit
if errorlevel 3 goto help
if errorlevel 2 goto nas_install
if errorlevel 1 goto kasse_install

:kasse_install
echo.
echo ================================================================================
echo   KASSENRECHNER-INSTALLATION
echo ================================================================================
echo.
echo   🚀 Starte vollautomatische Kassenrechner-Installation...
echo.
echo   Was wird installiert:
echo   ✅ Python Portable (falls nicht vorhanden)
echo   ✅ Wartungsmanager komplett eingerichtet
echo   ✅ Desktop-Icon "Wartungsmanager.bat"
echo   ✅ Auto-Start bei Windows-Boot
echo   ✅ Automatische NAS-Backups (alle 6h)
echo   ✅ Firewall-Konfiguration (Port 5000)
echo   ✅ iPad-Touch-Optimierung
echo.
echo   📍 Installation nach: C:\Wartungsmanager
echo   🌐 Zugriff über: http://localhost:5000
echo   💾 Backup nach: \\192.168.0.231\Tauchen\KompressorUeberwachung\backup
echo.
echo   Fortfahren mit der Installation?
choice /c JN /n /m "   [J]a oder [N]ein: "
if errorlevel 2 goto menu

echo.
echo   🔐 ADMINISTRATOR-RECHTE ERFORDERLICH
echo   Der Installer benötigt Administrator-Rechte für:
echo   - Python-Installation
echo   - Firewall-Konfiguration  
echo   - Auto-Start-Einrichtung
echo   - Task Scheduler (Backups)
echo.
pause
call "%~dp0setup_wartungsmanager.bat"
goto end

:nas_install
echo.
echo ================================================================================
echo   WD MY CLOUD NAS-INSTALLATION
echo ================================================================================
echo.
echo   🏢 Starte NAS-Installation...
echo.
echo   Was wird eingerichtet:
echo   ✅ Wartungsmanager-Dateien werden zur NAS kopiert
echo   ✅ NAS-Start-Script erstellt
echo   ✅ Client-Zugriff-Scripts für alle PCs
echo   ✅ Desktop-Icons für einfachen Zugriff
echo   ✅ iPad-Touch-Optimierung automatisch
echo.
echo   📍 NAS-Pfad: \\192.168.0.231\Tauchen\KompressorUeberwachung
echo   🌐 Zugriff über: http://192.168.0.231:5000
echo   💻 Client-Script: Automatischer Browser-Start
echo.
echo   ⚠️  VORAUSSETZUNG: Python muss auf der NAS installiert sein!
echo.
echo   Fortfahren mit der NAS-Installation?
choice /c JN /n /m "   [J]a oder [N]ein: "
if errorlevel 2 goto menu

echo.
pause
call "%~dp0setup_nas_deployment.bat"
goto end

:help
echo.
echo ================================================================================
echo   HILFE UND INFORMATIONEN
echo ================================================================================
echo.
echo   🤔 WELCHE OPTION SOLL ICH WÄHLEN?
echo.
echo   👍 KASSENRECHNER-INSTALLATION (Option 1) - EMPFOHLEN WENN:
echo      - Sie wollen die einfachste Installation
echo      - Der Kassenrechner läuft fast immer/24h
echo      - Sie wollen beste Performance
echo      - Sie brauchen keine zentrale NAS-Lösung
echo      - Sie wollen 1-Klick-Installation ohne Probleme
echo.
echo   🏢 NAS-INSTALLATION (Option 2) - EMPFOHLEN WENN:
echo      - Sie wollen zentrale Datenhaltung
echo      - Mehrere Kassenrechner gleichzeitig nutzen
echo      - Die NAS läuft 24/7 zuverlässiger als Kassenrechner
echo      - Sie haben Python-Kenntnisse für NAS-Setup
echo      - Sie wollen alle Daten zentral auf der NAS
echo.
echo   📱 IPAD-UNTERSTÜTZUNG:
echo      Beide Optionen unterstützen iPad vollständig:
echo      ✅ Popup-freie Bedienung (Problem vom 26.06.2025 gelöst!)
echo      ✅ Touch-optimierte Buttons (44px+ Touch-Targets)
echo      ✅ Inline-Formulare statt Modals
echo      ✅ Toast-Benachrichtigungen statt Popups
echo      ✅ Automatische iPad-Erkennung
echo.
echo   🔧 NACH DER INSTALLATION:
echo      Option 1: Doppelklick auf Desktop-Icon → Sofort einsatzbereit
echo      Option 2: start_nas_server.bat auf NAS → Clients per Browser
echo.
echo   💾 BACKUP-SYSTEM:
echo      Option 1: Automatische Backups zur NAS (alle 6h)
echo      Option 2: Daten direkt auf NAS (automatisch gesichert)
echo.
echo   🎯 UNSER TIPP: Wählen Sie Option 1 (Kassenrechner)!
echo      - Deutlich einfacher und zuverlässiger
echo      - Vollautomatische Installation
echo      - Backup zur NAS trotzdem vorhanden
echo      - Bei Problemen einfacher zu reparieren
echo.
pause
goto menu

:exit
echo.
echo ================================================================================
echo   INSTALLATION ABGEBROCHEN
echo ================================================================================
echo.
echo   Sie können die Installation jederzeit durch erneutes Ausführen
echo   dieser Datei starten.
echo.
echo   📁 Installer-Dateien verfügbar:
echo      - setup_wartungsmanager.bat (Kassenrechner)
echo      - setup_nas_deployment.bat (NAS)
echo      - ipad_zugriff.bat (iPad-Hilfe)
echo.
goto end

:end
echo.
echo   Drücken Sie eine Taste zum Beenden...
pause >nul
exit /b 0
