# Configuration für WartungsManager
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) # Project root

class Config:
    """Basis-Konfiguration für alle Umgebungen"""
    
    # Flask Core
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'wartungsmanager-dev-key-2025'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///C:/database/wartungsmanager.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Touch-UI Configuration
    TOUCH_BUTTON_MIN_SIZE = 44  # px - Apple Human Interface Guidelines
    TOUCH_SPACING = 8          # px - Minimum spacing between touch elements
    
    # Application Settings
    ITEMS_PER_PAGE = 20
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    
    # Session Configuration  
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)  # 8h Arbeitstag
    
    # Logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    
    # Email Configuration (für Wartungserinnerungen)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # PDF Generation
    PDF_TEMP_FOLDER = os.path.join(basedir, '..', 'temp', 'pdf')
    
    # Network Configuration
    DEFAULT_HOST = '0.0.0.0'  # Alle Interfaces
    DEFAULT_PORT = 5000
    SUGGESTED_IP = '192.168.0.50'  # Freie IP in FRITZ!Box Netzwerk
    
    # Shelly-Konfiguration
    SHELLY_CONFIG = {
        'enabled': os.environ.get('SHELLY_ENABLED', 'false').lower() in ['true', 'on', '1'],
        'ip_address': os.environ.get('SHELLY_IP'),
        'model': os.environ.get('SHELLY_MODEL', 'Shelly1PM'),
        'username': os.environ.get('SHELLY_USERNAME'),
        'password': os.environ.get('SHELLY_PASSWORD'),
        'timeout': int(os.environ.get('SHELLY_TIMEOUT', 10))
    }

    @staticmethod
    def init_app(app):
        """App-spezifische Initialisierung"""
        pass

class DevelopmentConfig(Config):
    """Development-spezifische Konfiguration"""
    DEBUG = True
    TESTING = False
    
    # Development Database (SQLite)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///C:/database/wartungsmanager.db'
    
    # Debug Toolbar
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

class TestingConfig(Config):
    """Testing-spezifische Konfiguration"""
    TESTING = True
    DEBUG = False
    
    # In-Memory Database für Tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # CSRF Protection deaktiviert für Tests
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production-spezifische Konfiguration"""
    DEBUG = False
    TESTING = False
    
    # Production Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///C:/database/wartungsmanager.db'
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    @classmethod
    def init_app(cls, app):
        """Production-spezifische App-Initialisierung"""
        Config.init_app(app)
        
        # Log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

# Konfiguration Dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Touch-UI Responsive Breakpoints
BREAKPOINTS = {
    'mobile': 768,    # Smartphone
    'tablet': 1024,   # Tablet 
    'desktop': 1200   # Desktop/Monitor
}

# UI Color Scheme (Touch-optimiert)
UI_COLORS = {
    'primary': '#007bff',     # Touch-safe Blue
    'success': '#28a745',     # Start-Button Green
    'danger': '#dc3545',      # Stop-Button Red  
    'warning': '#ffc107',     # Wartung Warning
    'info': '#17a2b8',        # Information
    'light': '#f8f9fa',       # Background
    'dark': '#343a40',        # Text
    'secondary': '#6c757d'    # Secondary Elements
}
