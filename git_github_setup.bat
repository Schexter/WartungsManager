@echo off
chcp 65001 > nul
echo ================================================================
echo           🔧 WARTUNGSMANAGER - GIT & GITHUB SETUP 🔧
echo ================================================================
echo.

:: Prüfe ob Git installiert ist
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ FEHLER: Git ist nicht installiert!
    echo.
    echo Bitte installiere Git von: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo ✅ Git ist installiert
echo.

:: Wechsle ins Projektverzeichnis
cd /d "C:\SoftwareProjekte\WartungsManager"

:: Initialisiere Git Repository
echo 📁 Initialisiere Git Repository...
git init
echo.

:: Konfiguriere Git (falls noch nicht geschehen)
echo 👤 Konfiguriere Git-Benutzer...
echo.
echo Bitte gib deine GitHub-Daten ein:
set /p GIT_USERNAME="GitHub Benutzername: "
set /p GIT_EMAIL="GitHub E-Mail: "

git config user.name "%GIT_USERNAME%"
git config user.email "%GIT_EMAIL%"
echo.

:: Füge alle Dateien hinzu
echo 📝 Füge Dateien zum Repository hinzu...
git add .
echo.

:: Erstelle ersten Commit
echo 💾 Erstelle initialen Commit...
git commit -m "Initial commit: WartungsManager - Produktionsreifes Flask-basiertes Wartungs- und Füllstandsmanagement-System"
echo.

echo ================================================================
echo           🌐 GITHUB REPOSITORY EINRICHTUNG 🌐
echo ================================================================
echo.
echo Nächste Schritte:
echo.
echo 1. Gehe zu https://github.com/new
echo 2. Erstelle ein neues Repository mit dem Namen: WartungsManager
echo 3. WICHTIG: Wähle "Private" oder "Public" nach deinem Wunsch
echo 4. NICHT initialisieren mit README, .gitignore oder License!
echo 5. Kopiere die Repository-URL (z.B. https://github.com/%GIT_USERNAME%/WartungsManager.git)
echo.
echo ----------------------------------------------------------------
echo.
set /p REPO_URL="Füge hier die GitHub Repository URL ein: "
echo.

:: Füge Remote hinzu
echo 🔗 Verbinde mit GitHub...
git remote add origin %REPO_URL%
echo.

:: Push zum Repository
echo 🚀 Lade Projekt zu GitHub hoch...
git branch -M main
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ================================================================
    echo                    ✅ ERFOLGREICH! ✅
    echo ================================================================
    echo.
    echo Dein WartungsManager ist jetzt auf GitHub!
    echo Repository: %REPO_URL%
    echo.
    echo Nützliche Git-Befehle:
    echo - Änderungen anzeigen: git status
    echo - Änderungen hinzufügen: git add .
    echo - Commit erstellen: git commit -m "Beschreibung"
    echo - Zu GitHub pushen: git push
    echo - Von GitHub pullen: git pull
    echo.
) else (
    echo.
    echo ❌ FEHLER beim Upload!
    echo.
    echo Mögliche Lösungen:
    echo 1. Stelle sicher, dass du bei GitHub angemeldet bist
    echo 2. Überprüfe die Repository-URL
    echo 3. Versuche: git push -u origin main --force
    echo.
)

pause

Erstellt von Hans Hahn - Alle Rechte vorbehalten
