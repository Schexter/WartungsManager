"""
Erweiterte Konfiguration für Shelly-Integration
Hier werden die Einstellungen für verschiedene Shelly-Modelle verwaltet
"""

class ShellyKonfiguration:
    """Zentrale Shelly-Konfigurationsklasse"""
    
    # Unterstützte Shelly-Modelle
    SUPPORTED_MODELS = {
        'Shelly1': {
            'name': 'Shelly 1 (Relais)',
            'api_type': 'gen1',
            'has_power_meter': False,
            'switch_url': '/relay/0',
            'status_url': '/status'
        },
        'Shelly1PM': {
            'name': 'Shelly 1PM (Relais + Leistungsmessung)',
            'api_type': 'gen1', 
            'has_power_meter': True,
            'switch_url': '/relay/0',
            'status_url': '/status'
        },
        'ShellyPlus1': {
            'name': 'Shelly Plus 1 (Gen2)',
            'api_type': 'gen2',
            'has_power_meter': False,
            'switch_url': '/rpc/Switch.Set',
            'status_url': '/rpc/Switch.GetStatus'
        },
        'ShellyPlus1PM': {
            'name': 'Shelly Plus 1PM (Gen2 + Leistungsmessung)',
            'api_type': 'gen2',
            'has_power_meter': True,
            'switch_url': '/rpc/Switch.Set',
            'status_url': '/rpc/Switch.GetStatus'
        }
    }
    
    @staticmethod
    def get_default_config():
        """Standard-Konfiguration zurückgeben"""
        return {
            'enabled': False,
            'ip_address': '192.168.1.100',
            'model': 'Shelly1PM',
            'username': '',
            'password': '', 
            'timeout': 10,
            'retry_attempts': 3,
            'kompressor_name': 'Kompressor'
        }
    
    @staticmethod
    def validate_config(config):
        """Konfiguration validieren"""
        errors = []
        
        if not config.get('ip_address'):
            errors.append('IP-Adresse erforderlich')
            
        if config.get('model') not in ShellyKonfiguration.SUPPORTED_MODELS:
            errors.append(f"Modell '{config.get('model')}' nicht unterstützt")
            
        # IP-Format prüfen
        ip = config.get('ip_address', '')
        if ip:
            parts = ip.split('.')
            if len(parts) != 4 or not all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
                errors.append('Ungültiges IP-Format')
        
        return errors

# Integration in Flask Config
def add_shelly_config_to_app(app):
    """Shelly-Konfiguration zur Flask-App hinzufügen"""
    
    # Standard-Konfiguration setzen falls nicht vorhanden
    if 'SHELLY_CONFIG' not in app.config:
        app.config['SHELLY_CONFIG'] = ShellyKonfiguration.get_default_config()
    
    # Validierung
    errors = ShellyKonfiguration.validate_config(app.config['SHELLY_CONFIG'])
    if errors:
        app.logger.warning(f"Shelly-Konfigurationsprobleme: {', '.join(errors)}")
    
    return app

# Erstellt von Hans Hahn - Alle Rechte vorbehalten
