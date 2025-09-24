@echo off
chcp 65001 > nul
echo ================================================================
echo    🔧 WARTUNGSMANAGER - GIT KOMMANDOZEILEN SETUP 🔧
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
git --version
echo.

:: Wechsle ins Projektverzeichnis
cd /d "C:\SoftwareProjekte\WartungsManager"
echo 📁 Arbeitsverzeichnis: %CD%
echo.

:: Git initialisieren
echo 🔧 Initialisiere Git Repository...
git init
echo.

:: Git Konfiguration
echo 👤 Aktuelle Git-Konfiguration:
git config --list | findstr user
echo.

:: Setze Benutzerdaten falls nicht vorhanden
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo Keine Git-Benutzerdaten gefunden. Bitte konfigurieren:
    set /p GIT_NAME="Dein Name: "
    set /p GIT_EMAIL="Deine E-Mail: "
    git config --global user.name "!GIT_NAME!"
    git config --global user.email "!GIT_EMAIL!"
    echo ✅ Git-Benutzerdaten gesetzt
    echo.
)

:: Status anzeigen
echo 📊 Repository Status:
git status --short
echo.

:: Dateien zum Staging hinzufügen
echo 📝 Füge alle Dateien zum Staging-Bereich hinzu...
git add .
echo.

:: Zeige was committed wird
echo 📋 Folgende Dateien werden committed:
git status --short
echo.

:: Commit erstellen
echo 💾 Erstelle Initial Commit...
git commit -m "Initial commit: WartungsManager v2.0 - Produktionsreifes Wartungs- und Füllstandsmanagement-System

Features:
- Flask-basierte Web-Anwendung (Python 3.11)
- Touch-optimierte UI für iPad/Tablet
- SQLite Datenbank mit Auto-Migration
- 62mm Thermodrucker Integration (ESC/POS)
- Automatisches NAS-Backup
- Kompressor-Steuerung und Protokollierung
- Multi-Client-fähig im Netzwerk
- Vollautomatische Windows-Installer

Technologie-Stack:
- Backend: Python 3.11 + Flask 2.3.3
- Frontend: HTML5 + Bootstrap 5
- Datenbank: SQLite + Alembic
- Deployment: Windows Service + Auto-Start

Status: PRODUKTIONSREIF"

echo.
echo ✅ Initial Commit erstellt!
echo.

:: Branch umbenennen
echo 🌿 Benenne Branch zu 'main' um...
git branch -M main
echo.

:: GitHub Remote hinzufügen
echo ================================================================
echo              🌐 GITHUB REMOTE EINRICHTEN 🌐
echo ================================================================
echo.
echo OPTION 1: Neues Repository auf GitHub erstellen
echo -----------------------------------------------
echo 1. Öffne https://github.com/new in deinem Browser
echo 2. Repository Name: WartungsManager
echo 3. Beschreibung: "Produktionsreifes Wartungs- und Füllstandsmanagement-System"
echo 4. Wähle Private/Public nach Wunsch
echo 5. WICHTIG: KEINE Initialisierung mit README/.gitignore/License!
echo 6. Klicke "Create repository"
echo.
echo OPTION 2: Bestehendes Repository verwenden
echo ------------------------------------------
echo Verwende die URL deines bestehenden Repositories
echo.
echo Format: https://github.com/BENUTZERNAME/WartungsManager.git
echo     oder: git@github.com:BENUTZERNAME/WartungsManager.git
echo.
set /p REMOTE_URL="GitHub Repository URL eingeben (oder Enter für später): "

if not "!REMOTE_URL!"=="" (
    echo.
    echo 🔗 Füge GitHub als Remote hinzu...
    git remote add origin !REMOTE_URL!
    
    echo.
    echo 🚀 Pushe zu GitHub...
    git push -u origin main
    
    if !errorlevel! equ 0 (
        echo.
        echo ✅ ERFOLGREICH zu GitHub gepusht!
        echo.
        echo Repository URL: !REMOTE_URL!
    ) else (
        echo.
        echo ⚠️  Push fehlgeschlagen. Mögliche Gründe:
        echo    - Repository existiert nicht
        echo    - Keine Berechtigung
        echo    - Falscher URL
        echo.
        echo Versuche manuell:
        echo    git remote set-url origin NEUE_URL
        echo    git push -u origin main
    )
) else (
    echo.
    echo ℹ️  Remote-Setup übersprungen. Du kannst es später hinzufügen mit:
    echo    git remote add origin https://github.com/DEINNAME/WartungsManager.git
    echo    git push -u origin main
)

echo.
echo ================================================================
echo                   📚 NÜTZLICHE GIT BEFEHLE 📚
echo ================================================================
echo.
echo ALLTÄGLICHE BEFEHLE:
echo   git status              - Zeige Änderungen
echo   git add .               - Füge alle Änderungen hinzu
echo   git commit -m "Text"    - Erstelle Commit
echo   git push                - Lade zu GitHub hoch
echo   git pull                - Hole Änderungen von GitHub
echo.
echo BRANCHES:
echo   git branch              - Zeige Branches
echo   git checkout -b neu     - Erstelle neuen Branch
echo   git merge branch        - Merge Branch
echo.
echo HISTORIE:
echo   git log --oneline       - Zeige Commit-Historie
echo   git diff                - Zeige Unterschiede
echo.
echo ================================================================
echo.
pause

Erstellt von Hans Hahn - Alle Rechte vorbehalten
