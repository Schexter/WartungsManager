@echo off
echo.
echo 🔧 KOMPRESSOR-REPARATUR AUTOMATISCH
echo =====================================
echo.

cd /d "C:\SoftwareProjekte\WartungsManager\Source\Python"

echo 1. Aktiviere virtuelle Umgebung...
call wartung_env\Scripts\activate.bat

echo.
echo 2. Führe Datenbank-Migration aus...
python -c "from flask_migrate import upgrade; from app import create_app; app = create_app(); app.app_context().push(); upgrade()"

echo.
echo 3. Führe Kompressor-Reparatur aus...
python fix_kompressor_issues.py

echo.
echo 🎯 Automatische Reparatur abgeschlossen!
echo.
echo ▶️ Starten Sie jetzt den Server neu:
echo    python run.py
echo.
pause
