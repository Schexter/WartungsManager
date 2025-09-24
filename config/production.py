# Produktions-Konfiguration für NAS-Deployment
# config/production.py

import os
from datetime import timedelta

class ProductionConfig:
    """Produktions-Konfiguration für NAS-Hosting"""
    
    # ============================================================================
    # SERVER-KONFIGURATION
    # ============================================================================
    
    # Netzwerk
    HOST = '0.0.0.0'  # Alle Netzwerk-Interfaces (NAS erreichbar aus Netzwerk)
    PORT = 5000       # Standard-Port (in Firewall freigeben!)
    
    # Flask
    DEBUG = False                    # Keine Debug-Informationen in Produktion
    TESTING = False                  # Kein Test-Modus
    ENV = 'production'               # Produktionsumgebung
    
    # ============================================================================
    # DATENBANK-KONFIGURATION
    # ============================================================================
    
    # SQLite-Datenbank (lokal auf NAS)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database/wartungsmanager.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,       # Verbindung vor Nutzung prüfen
        'pool_recycle': 300,         # Verbindung alle 5 Min erneuern
        'connect_args': {
            'check_same_thread': False,  # Für Multi-Client-Zugriff
            'timeout': 10                # 10s Timeout für DB-Operationen
        }
    }
    
    # ============================================================================
    # SICHERHEIT
    # ============================================================================
    
    # Secret Key für Sessions (ÄNDERN SIE DIESEN WERT!)
    SECRET_KEY = 'Magicfactory15!_NAS_PRODUCTION_2025'
    
    # Session-Konfiguration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)  # 8h Session-Dauer
    SESSION_COOKIE_SECURE = False     # HTTP (nicht HTTPS) auf NAS
    SESSION_COOKIE_HTTPONLY = True    # Kein JavaScript-Zugriff auf Cookies
    SESSION_COOKIE_SAMESITE = 'Lax'   # CSRF-Schutz
    
    # Wartungs-Passwort (wie bisher)
    MAINTENANCE_PASSWORD = 'Magicfactory15!'
    
    # ============================================================================
    # LOGGING & MONITORING
    # ============================================================================
    
    # Log-Dateien
    LOG_FILE = 'logs/production.log'
    ERROR_LOG_FILE = 'logs/error.log'
    ACCESS_LOG_FILE = 'logs/access.log'
    
    # Log-Level
    LOG_LEVEL = 'INFO'               # INFO, WARNING, ERROR
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB pro Log-Datei
    LOG_BACKUP_COUNT = 5             # 5 Backup-Dateien behalten
    
    # Performance-Monitoring
    SLOW_DB_QUERY_TIME = 0.5        # Langsame Queries > 0.5s loggen
    
    # ============================================================================
    # BACKUP & WARTUNG
    # ============================================================================
    
    # Backup-Konfiguration
    BACKUP_DIR = 'logs/backups'
    BACKUP_INTERVAL_HOURS = 6        # Backup alle 6 Stunden
    BACKUP_RETENTION_DAYS = 30       # Backups 30 Tage behalten
    
    # Auto-Cleanup
    AUTO_CLEANUP_LOGS_DAYS = 7       # Logs älter 7 Tage löschen
    AUTO_CLEANUP_TEMP_FILES = True   # Temp-Dateien automatisch löschen
    
    # ============================================================================
    # FEATURES & LIMITS
    # ============================================================================
    
    # Upload-Limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max Upload
    
    # Rate-Limiting (gegen DoS)
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # ============================================================================
    # NAS-SPEZIFISCHE EINSTELLUNGEN
    # ============================================================================
    
    # Multi-Client Support
    ALLOW_MULTIPLE_CLIENTS = True
    MAX_CONCURRENT_CLIENTS = 10
    
    # iPad/Touch-Optimierung
    ENABLE_TOUCH_OPTIMIZATION = True
    IPAD_MODE_AUTO_DETECT = True
    
    # Netzwerk-Timeout
    REQUEST_TIMEOUT = 30             # 30s Request-Timeout
    KEEP_ALIVE_TIMEOUT = 5           # 5s Keep-Alive
    
    # ============================================================================
    # CACHE & PERFORMANCE
    # ============================================================================
    
    # Static-File Caching
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(hours=1)  # 1h Cache für CSS/JS
    
    # Template-Caching
    TEMPLATES_AUTO_RELOAD = False    # Templates nicht auto-reloaden
    
    # JSON-Komprimierung
    JSONIFY_PRETTYPRINT_REGULAR = False  # Kompakte JSON-Antworten
    
    # ============================================================================
    # DEVELOPMENT/DEBUG (für Problemdiagnose)
    # ============================================================================
    
    # Erweiterte Fehler-Informationen (nur bei Problemen aktivieren)
    PROPAGATE_EXCEPTIONS = True
    TRAP_HTTP_EXCEPTIONS = False
    TRAP_BAD_REQUEST_ERRORS = False
    
    # SQL-Query-Logging (nur für Debugging)
    SQLALCHEMY_RECORD_QUERIES = False
    DATABASE_QUERY_TIMEOUT = 10.0
    
    # ============================================================================
    # PRINT-SYSTEM (62mm Drucker)
    # ============================================================================
    
    # Drucker-Konfiguration
    PRINTER_DEFAULT_INTERFACE = 'usb'
    PRINTER_USB_VENDOR_ID = 0x04b8    # Epson
    PRINTER_USB_PRODUCT_ID = 0x0202
    
    # Print-Job Limits
    MAX_PRINT_JOBS_PER_MINUTE = 10
    PRINT_JOB_TIMEOUT = 30
    
    # ============================================================================
    # HEALTH-CHECK & MONITORING
    # ============================================================================
    
    # Health-Check Endpoint
    HEALTH_CHECK_ENABLED = True
    HEALTH_CHECK_ENDPOINT = '/health'
    
    # System-Monitoring
    MONITOR_SYSTEM_RESOURCES = True
    MONITOR_DATABASE_SIZE = True
    MONITOR_LOG_SIZE = True
    
    # Alerting (bei kritischen Fehlern)
    ALERT_ON_DATABASE_ERROR = True
    ALERT_ON_DISK_FULL = True
    ALERT_EMAIL = None  # Email für Alerts (optional)


# ============================================================================
# CONFIGURATION MAPPING
# ============================================================================

config = {
    'development': ProductionConfig,
    'testing': ProductionConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
