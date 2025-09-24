# WartungsManager Flask Application Factory
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config.config import config

# Globale Objekte
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name='default'):
    """
    Flask Application Factory Pattern
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Extensions initialisieren
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Login Manager Settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Bitte loggen Sie sich ein, um auf diese Seite zugreifen zu können.'
    login_manager.login_message_category = 'info'

    # Models importieren
    from app import models

    # Blueprints registrieren
    from .routes.main import main_bp
    app.register_blueprint(main_bp)
    
    from .routes.fuelling import bp as fuelling_bp
    app.register_blueprint(fuelling_bp, url_prefix='/fuelling')

    from .routes.kompressor import bp as kompressor_bp
    app.register_blueprint(kompressor_bp, url_prefix='/kompressor')
    
    from .routes.maintenance import bp as maintenance_bp
    app.register_blueprint(maintenance_bp, url_prefix='/maintenance')

    from .routes.maintenance_api import bp as maintenance_api_bp
    app.register_blueprint(maintenance_api_bp)
    
    from .routes.protocol import bp as protocol_bp
    app.register_blueprint(protocol_bp, url_prefix='/protocol')
    
    from .routes.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from .routes.kompressor_api import bp as kompressor_api_bp
    app.register_blueprint(kompressor_api_bp)
    
    from .routes.flaschen_api import bp as flaschen_api_bp
    app.register_blueprint(flaschen_api_bp)
    
    from .routes.kunden_api import bp as kunden_api_bp
    app.register_blueprint(kunden_api_bp)

    # Shelly IoT Integration
    try:
        from .routes.shelly import shelly_bp
        app.register_blueprint(shelly_bp)
        app.logger.info("✅ Shelly-Integration geladen (/shelly)")
        
        # Kompressor-Shelly Integration
        from .routes.kompressor_shelly_api import kompressor_shelly_bp
        app.register_blueprint(kompressor_shelly_bp)
        app.logger.info("✅ Kompressor-Shelly API geladen")
    except ImportError as e:
        app.logger.warning(f"Shelly-Modul nicht gefunden: {e}")
    except Exception as e:
        app.logger.error(f"Fehler beim Laden des Shelly-Moduls: {e}")

    # K14 Dokumentation
    from .routes.k14_routes import bp as k14_bp
    app.register_blueprint(k14_bp)

    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    try:
        from .routes.admin import admin_bp
        app.register_blueprint(admin_bp)
    except ImportError:
        app.logger.warning("Admin-Modul nicht gefunden.")

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return "<h1>404 - Seite nicht gefunden</h1>", 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return "<h1>500 - Server-Fehler</h1>", 500
    
    return app
