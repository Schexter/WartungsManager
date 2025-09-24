#!/usr/bin/env python3
"""
Wartungsmanager Flask Application - Production Runner
Optimiert für NAS-Deployment mit Multi-Client-Support
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Projekt-Pfad zur Python-Path hinzufügen
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate
    
    # Lokale Imports
    from app import create_app
    from config.production import ProductionConfig, validate_config
    
except ImportError as e:
    print(f"❌ FEHLER: Benötigte Python-Pakete nicht gefunden: {e}")
    print("Führen Sie aus: pip install -r requirements.txt")
    sys.exit(1)


def setup_production_logging():
    """Produktions-Logging konfigurieren"""
    
    # Log-Verzeichnis erstellen
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Root-Logger konfigurieren
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/production.log', encoding='utf-8'),
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
    
    # Erforderliche Verzeichnisse prüfen
    required_dirs = ['database', 'logs', 'logs/backups', 'app/templates', 'app/static']
    for directory in required_dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Datenbank-Datei prüfen
    db_path = Path('database/wartungsmanager.db')
    if not db_path.exists():
        logger.warning("Datenbank-Datei nicht gefunden - wird bei erstem Start erstellt")
    
    return True


def create_production_app():
    """Produktions-App erstellen"""
    
    logger = logging.getLogger(__name__)
    
    try:
        # Konfiguration validieren
        validate_config(ProductionConfig)
        
        # Flask-App erstellen
        app = create_app(config_class=ProductionConfig)
        
        # Produktions-spezifische Konfiguration
        app.config.update(
            # Performance-Optimierungen
            SEND_FILE_MAX_AGE_DEFAULT=3600,  # 1h Cache für statische Dateien
            
            # Sicherheit
            SESSION_COOKIE_SECURE=False,     # HTTP (nicht HTTPS) auf NAS
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='Lax',
            
            # Multi-Client Support
            SQLALCHEMY_ENGINE_OPTIONS={
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'connect_args': {
                    'check_same_thread': False,  # Wichtig für SQLite + Multi-Client
                    'timeout': 10
                }
            }
        )
        
        logger.info("✅ Produktions-App erfolgreich erstellt")
        return app
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Erstellen der App: {e}")
        raise


def run_development():
    """Development-Modus (für lokale Tests)"""
    
    logger = logging.getLogger(__name__)
    
    try:
        app = create_app()
        
        logger.info("🔧 DEVELOPMENT-MODUS")
        logger.info(f"🌐 Server: http://127.0.0.1:5000")
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


def run_production():
    """Produktions-Modus (für NAS-Deployment)"""
    
    logger = logging.getLogger(__name__)
    
    try:
        app = create_production_app()
        
        # Startup-Informationen
        logger.info("🚀 PRODUKTIONS-MODUS GESTARTET")
        logger.info("=" * 50)
        logger.info(f"🌐 Host: {ProductionConfig.HOST}")
        logger.info(f"🔌 Port: {ProductionConfig.PORT}")
        logger.info(f"💾 Datenbank: {ProductionConfig.SQLALCHEMY_DATABASE_URI}")
        logger.info(f"📝 Log-Level: {ProductionConfig.LOG_LEVEL}")
        logger.info(f"🔒 Debug: {ProductionConfig.DEBUG}")
        logger.info("=" * 50)
        logger.info("📱 Multi-Client Support: Aktiviert")
        logger.info("🍎 iPad-Kompatibilität: Aktiviert")
        logger.info("🖨️  Drucker-Integration: Verfügbar")
        logger.info("=" * 50)
        logger.info("🌐 Zugriff von Clients:")
        logger.info(f"   💻 Kasse: wartungsmanager_kasse.bat")
        logger.info(f"   📱 iPad: http://{get_local_ip()}:{ProductionConfig.PORT}")
        logger.info(f"   🌐 Browser: http://{get_local_ip()}:{ProductionConfig.PORT}")
        logger.info("=" * 50)
        logger.info("⏹️  CTRL+C zum Beenden")
        logger.info("")
        
        # Automatisches Backup bei Start
        try:
            run_backup()
        except Exception as e:
            logger.warning(f"Startup-Backup fehlgeschlagen: {e}")
        
        # Flask-Server starten
        app.run(
            host=ProductionConfig.HOST,
            port=ProductionConfig.PORT,
            debug=ProductionConfig.DEBUG,
            threaded=True,          # Multi-Threading für mehrere Clients
            use_reloader=False,     # Kein Auto-Reload in Produktion
            processes=1             # Single-Process für SQLite-Kompatibilität
        )
        
    except KeyboardInterrupt:
        logger.info("⏹️  Server durch Benutzer beendet")
    except Exception as e:
        logger.error(f"❌ Produktions-Server Fehler: {e}")
        raise
    finally:
        logger.info("🔄 Server beendet")


def get_local_ip():
    """Lokale IP-Adresse ermitteln"""
    
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "localhost"


def run_backup():
    """Schnelles Datenbank-Backup bei Server-Start"""
    
    logger = logging.getLogger(__name__)
    
    try:
        import shutil
        from datetime import datetime
        
        # Backup-Pfade
        source_db = Path('database/wartungsmanager.db')
        backup_dir = Path('logs/backups')
        backup_dir.mkdir(exist_ok=True)
        
        if source_db.exists():
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_file = backup_dir / f"startup_backup_{timestamp}.db"
            
            shutil.copy2(source_db, backup_file)
            logger.info(f"💾 Startup-Backup erstellt: {backup_file.name}")
            
            # Dateigröße loggen
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            logger.info(f"📊 Backup-Größe: {size_mb:.2f} MB")
            
        else:
            logger.warning("⚠️  Keine Datenbank für Backup gefunden")
            
    except Exception as e:
        logger.warning(f"Backup-Fehler: {e}")


if __name__ == '__main__':
    
    # Logging setup
    logger = setup_production_logging()
    
    # System-Check
    if not check_system_requirements():
        sys.exit(1)
    
    # Ausführungs-Modus bestimmen
    if len(sys.argv) > 1 and sys.argv[1] == 'dev':
        # Development-Modus
        run_development()
    else:
        # Standard: Produktions-Modus
        run_production()
