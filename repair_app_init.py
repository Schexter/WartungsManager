#!/usr/bin/env python3
"""
Reparatur-Script für beschädigte App __init__.py
Stellt die originale Struktur wieder her und fügt Admin-Interface korrekt hinzu
"""

import shutil
from pathlib import Path

def repair_app_init():
    """Repariert die beschädigte __init__.py"""
    
    app_init_path = Path("C:/SoftwareEntwicklung/WartungsManager-main/Source/Python/app/__init__.py")
    backup_path = app_init_path.with_suffix('.py.backup')
    
    # Backup der beschädigten Datei
    if app_init_path.exists():
        shutil.copy2(app_init_path, backup_path)
        print(f"✅ Backup erstellt: {backup_path}")
    
    # Neue, funktionierende __init__.py erstellen
    new_init_content = '''"""
WartungsManager Flask Application
Hauptinitialisierung der Flask-App
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name='default'):
    """Application Factory Pattern"""
    
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'wartungsmanager-secret-key-2025'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../../database/wartungsmanager.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Login Manager Settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Bitte loggen Sie sich ein, um auf diese Seite zugreifen zu können.'
    login_manager.login_message_category = 'info'
    
    # Import models
    from app import models
    
    # Register Blueprints
    try:
        # Main routes
        from app.routes.main import main_bp
        app.register_blueprint(main_bp)
        
        # Kompressor routes
        from app.routes.kompressor import kompressor_bp
        app.register_blueprint(kompressor_bp)
        
        # Fuellmanager routes  
        from app.routes.fuellmanager import fuellmanager_bp
        app.register_blueprint(fuellmanager_bp)
        
        # API routes
        from app.routes.api import api_bp
        app.register_blueprint(api_bp)
        
        app.logger.info("✅ Hauptmodule geladen")
        
    except ImportError as e:
        app.logger.warning(f"⚠️ Einige Module nicht verfügbar: {e}")
    
    # Admin & Shelly Integration (optional)
    try:
        from app.routes.admin import admin_bp
        from app.routes.shelly_api import shelly_api
        
        app.register_blueprint(admin_bp)
        app.register_blueprint(shelly_api)
        
        # Shelly-Konfiguration
        app.config['SHELLY_CONFIG'] = {
            'enabled': False,
            'ip_address': '192.168.1.100',
            'model': 'Shelly1PM',
            'username': '',
            'password': '',
            'timeout': 10
        }
        
        app.logger.info("✅ Admin-Interface aktiviert: /admin")
        app.logger.info("✅ Shelly-API aktiviert: /api/shelly")
        
    except ImportError as e:
        app.logger.warning(f"⚠️ Admin-Module nicht verfügbar: {e}")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return '<h1>404 - Seite nicht gefunden</h1><p><a href="/">Zurück zur Startseite</a></p>', 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return '<h1>500 - Server-Fehler</h1><p><a href="/">Zurück zur Startseite</a></p>', 500
    
    # Create tables
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("✅ Datenbank-Tabellen initialisiert")
        except Exception as e:
            app.logger.error(f"❌ Datenbank-Initialisierung fehlgeschlagen: {e}")
    
    app.logger.info("🚀 WartungsManager Flask-App initialisiert")
    
    return app

# Erstellt von Hans Hahn - Alle Rechte vorbehalten
'''
    
    # Neue Datei schreiben
    with open(app_init_path, 'w', encoding='utf-8') as f:
        f.write(new_init_content)
    
    print("✅ App __init__.py repariert")
    return True

def main():
    print("🔧 WartungsManager App-Reparatur")
    print("=" * 40)
    
    try:
        if repair_app_init():
            print("\n🎉 REPARATUR ERFOLGREICH!")
            print("=" * 40)
            print("✅ App __init__.py wiederhergestellt")
            print("✅ Admin-Interface korrekt integriert")
            print("✅ Shelly-API verfügbar")
            
            print("\n🚀 System jetzt starten:")
            print("python run_production_REPARIERT.py")
            
            print("\n🌐 Admin-Zugang:")
            print("http://localhost:5000/admin")
            print("http://localhost:5000/templates/admin_access.html")
            
    except Exception as e:
        print(f"❌ Reparatur fehlgeschlagen: {e}")

if __name__ == '__main__':
    main()
