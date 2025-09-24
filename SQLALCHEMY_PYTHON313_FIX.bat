@echo off
title WartungsManager - SQLALCHEMY PYTHON 3.13 FIX
color 0A
echo =========================================================
echo   WARTUNGSMANAGER - SQLALCHEMY PYTHON 3.13 FIX
echo =========================================================
echo   Behebt: SQLAlchemy Kompatibilitätsproblem
echo   Erstellt von Hans Hahn - Alle Rechte vorbehalten
echo =========================================================
echo.

cd /d "C:\SoftwareEntwicklung\WartungsManager-main"

echo 📁 Arbeitsverzeichnis: %CD%
echo 🐍 Python-Version:
python --version
echo.

echo 🔧 SQLAlchemy auf Python 3.13 kompatible Version upgraden...
echo ⚠️ Problem: SQLAlchemy 2.0.21 ist nicht kompatibel mit Python 3.13
echo ✅ Lösung: Upgrade auf SQLAlchemy 2.0.23+
echo.

REM SQLAlchemy und Flask-SQLAlchemy upgraden
echo 📦 Upgrading SQLAlchemy...
pip install --upgrade SQLAlchemy>=2.0.23
if errorlevel 1 (
    echo ❌ SQLAlchemy-Upgrade fehlgeschlagen!
    echo 💡 Versuche spezifische Version...
    pip install SQLAlchemy==2.0.25
)

echo.
echo 📦 Upgrading Flask-SQLAlchemy...
pip install --upgrade Flask-SQLAlchemy>=3.1.0
if errorlevel 1 (
    echo ❌ Flask-SQLAlchemy-Upgrade fehlgeschlagen!
    echo 💡 Versuche spezifische Version...
    pip install Flask-SQLAlchemy==3.1.1
)

echo.
echo 📦 Upgrading Alembic (für Migrations)...
pip install --upgrade Alembic>=1.13.0

echo.
echo =========================================================
echo   SQLALCHEMY PYTHON 3.13 FIX ABGESCHLOSSEN!
echo =========================================================
echo.
echo ✅ SQLAlchemy ist jetzt Python 3.13 kompatibel!
echo.
echo 🚀 SYSTEM JETZT STARTEN:
echo    python run_production_REPARIERT.py
echo.
echo 🌐 Nach dem Start:
echo    http://localhost:5000
echo.
pause
