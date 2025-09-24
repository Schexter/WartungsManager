#!/usr/bin/env python3
"""
Wartungsmanager Flask Application - Production Runner (REPARIERT)
Behebt: No module named 'app' Fehler
Erstellt von Hans Hahn - Alle Rechte vorbehalten
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

def setup_python_paths():
    """Python-Pfade für WartungsManager konfigurieren"""
    
    project_root = Path(__file__).parent.absolute()
    
    # KRITISCH: Source/Python-Verzeichnis zum Python-Path hinzufügen
    source_python_path = project_root / "Source" / "Python"
    
    if source_python_path.exists():
        sys.path.insert(0, str(source_python_path))
        print(f"✅ Python-Pfad hinzugefügt: {source_python_path}")
    else:
        print(f"❌ FEHLER: Source/Python Verzeichnis nicht gefunden!")
        print(f"   Erwartet: {source_python_path}")
        return False
    
    # Arbeitsverzeichnis setzen
    os.chdir(source_python_path)
    print(f"✅ Arbeitsverzeichnis: {os.getcwd()}")
    
    return True

def test_imports():
    """Teste alle kritischen Imports"""
    
    print("\n🔍 Teste Python-Imports...")
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError as e:
        print(f"❌ Flask-Import fehlgeschlagen: {e}")
        return False
    
    try:
        import app
        print(f"✅ App-Modul gefunden: {app}")
    except ImportError as e:
        print(f"❌ App-Import fehlgeschlagen: {e}")
        print("💡 Tipp: Prüfen Sie ob Source/Python/app/__init__.py existiert")
        return False
    
    try:
        from app import create_app
        print("✅ create_app Funktion gefunden")
    except ImportError as e:
        print(f"❌ create_app Import fehlgeschlagen: {e}")
        return False
    
    return True

def setup_production_logging():
    """Produktions-Logging konfigurieren"""
    
    # Log-Verzeichnis erstellen (relativ zum Source/Python)
    log_dir = Path('../../logs')  # Zurück zum Hauptverzeichnis
    log_dir.mkdir(exist_ok=True)
    
    # Root-Logger konfigurieren
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'production.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Flask-Logger anpassen
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

def check_system_requirements():
    """System-Anforderungen prüfen"""
    
    logger = logging.getLogger(__name__)
    
    # Python-Version prüfen
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 oder höher erforderlich!")
        return False
    
    # Erforderliche Verzeichnisse prüfen (relativ zu Hauptverzeichnis)
    base_path = Path("../..")  # Zurück zum WartungsManager-main
    required_dirs = [
        base_path / 'database', 
        base_path / 'logs', 
        base_path / 'logs' / 'backups'
    ]
    
    for directory in required_dirs:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Verzeichnis sichergestellt: {directory}")
    
    return True

def get_local_ip():
    """Lokale IP-Adresse ermitteln"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "localhost"

def run_production():
    """Produktions-Modus starten"""
    
    logger = logging.getLogger(__name__)
    
    try:
        # App importieren und erstellen
        from app import create_app
        
        # App mit Standard-Konfiguration erstellen
        app = create_app()
        
        # Produktions-spezifische Konfiguration
        app.config.update({
            'DEBUG': False,
            'TESTING': False,
            'ENV': 'production',
            'SEND_FILE_MAX_AGE_DEFAULT': 3600,
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax',
        })
        
        # Startup-Informationen
        local_ip = get_local_ip()
        
        logger.info("🚀 WARTUNGSMANAGER PRODUCTION SERVER")
        logger.info("=" * 50)
        logger.info(f"🌐 Lokaler Zugriff: http://localhost:5000")
        logger.info(f"🌐 Netzwerk-Zugriff: http://{local_ip}:5000")
        logger.info(f"📱 iPad/Mobile: http://{local_ip}:5000")
        logger.info(f"🐍 Python Version: {sys.version}")
        logger.info("=" * 50)
        logger.info("📱 Features aktiv:")
        logger.info("  ✅ Multi-Client Support")
        logger.info("  ✅ iPad Touch-UI")
        logger.info("  ✅ Popup-freie Bedienung")
        logger.info("  ✅ 62mm Drucker-Support")
        logger.info("=" * 50)
        logger.info("⏹️  CTRL+C zum Beenden")
        logger.info("")
        
        # Flask-Server starten
        app.run(
            host='0.0.0.0',          # Alle Netzwerk-Interfaces
            port=5000,               # Standard-Port
            debug=False,             # Production-Modus
            threaded=True,           # Multi-Threading
            use_reloader=False       # Kein Auto-Reload
        )
        
    except KeyboardInterrupt:
        logger.info("⏹️  Server durch Benutzer beendet")
    except Exception as e:
        logger.error(f"❌ Server-Fehler: {e}")
        logger.error(f"📝 Fehlertyp: {type(e).__name__}")
        import traceback
        logger.error(f"📋 Stack Trace:\n{traceback.format_exc()}")
        raise

def run_development():
    """Development-Modus für Tests"""
    
    logger = logging.getLogger(__name__)
    
    try:
        from app import create_app
        app = create_app()
        
        logger.info("🔧 DEVELOPMENT-MODUS")
        logger.info("🌐 Server: http://127.0.0.1:5000")
        logger.info("🔥 Hot-Reload aktiviert")
        
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            threaded=True,
            use_reloader=True
        )
        
    except Exception as e:
        logger.error(f"❌ Development-Server Fehler: {e}")
        raise

def main():
    """Hauptfunktion mit Fehlerbehandlung"""
    
    print("🔧 WartungsManager Startup...")
    print(f"📁 Projekt-Verzeichnis: {Path(__file__).parent}")
    
    # Schritt 1: Python-Pfade konfigurieren
    if not setup_python_paths():
        print("❌ KRITISCHER FEHLER: Python-Pfad-Konfiguration fehlgeschlagen")
        input("Drücken Sie Enter zum Beenden...")
        return False
    
    # Schritt 2: Imports testen
    if not test_imports():
        print("❌ KRITISCHER FEHLER: Import-Test fehlgeschlagen")
        print("\n💡 LÖSUNGSVORSCHLÄGE:")
        print("1. pip install -r requirements_production.txt")
        print("2. Prüfen Sie ob Source/Python/app/ existiert")
        print("3. setup_wartungsmanager_v2.bat ausführen")
        input("Drücken Sie Enter zum Beenden...")
        return False
    
    # Schritt 3: Logging setup
    logger = setup_production_logging()
    
    # Schritt 4: System-Check
    if not check_system_requirements():
        logger.error("System-Requirements nicht erfüllt")
        return False
    
    # Schritt 5: Server starten
    try:
        # Ausführungs-Modus bestimmen
        if len(sys.argv) > 1 and sys.argv[1] == 'dev':
            run_development()
        else:
            run_production()
        return True
        
    except Exception as e:
        logger.error(f"❌ Kritischer Server-Fehler: {e}")
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        input("\n❌ Fehler aufgetreten. Drücken Sie Enter zum Beenden...")
        sys.exit(1)
