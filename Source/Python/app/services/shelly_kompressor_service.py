#!/usr/bin/env python3
"""
Shelly Integration Service für WartungsManager
Universelle API-Lösung für verschiedene Shelly-Modelle
"""

import requests
import logging
from typing import Optional, Dict, Any
import json
from datetime import datetime

class ShellyController:
    """Universeller Shelly-Controller"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def validate_config(self) -> bool:
        """Konfiguration validieren"""
        required_fields = ['ip_address', 'model', 'username', 'password']
        
        for field in required_fields:
            if field not in self.config:
                self.logger.error(f"Fehlende Konfiguration: {field}")
                return False
                
        return True
    
    def get_status(self) -> Optional[Dict[str, Any]]:
        """Aktuellen Status abfragen"""
        
        if not self.validate_config():
            return None
            
        try:
            url = f"http://{self.config['ip_address']}/status"
            
            response = requests.get(
                url,
                auth=(self.config.get('username'), self.config.get('password')),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Universelle Status-Auswertung
                status_info = {
                    'online': True,
                    'timestamp': datetime.now().isoformat(),
                    'model': self.config['model'],
                    'ip': self.config['ip_address']
                }
                
                # Modell-spezifische Status-Extraktion
                if self.config['model'].startswith('Shelly1'):
                    status_info['relay_on'] = data.get('relays', [{}])[0].get('ison', False)
                    status_info['power'] = data.get('meters', [{}])[0].get('power', 0)
                    
                elif self.config['model'].startswith('ShellyPlus'):
                    status_info['relay_on'] = data.get('switch:0', {}).get('output', False)
                    status_info['power'] = data.get('switch:0', {}).get('apower', 0)
                    
                return status_info
                
            else:
                self.logger.error(f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Fehler beim Status-Abruf: {e}")
            return {'online': False, 'error': str(e)}
    
    def turn_on(self) -> bool:
        """Shelly einschalten"""
        return self._switch_relay(True)
    
    def turn_off(self) -> bool:
        """Shelly ausschalten"""
        return self._switch_relay(False)
    
    def _switch_relay(self, state: bool) -> bool:
        """Relais schalten"""
        
        if not self.validate_config():
            return False
            
        try:
            # Modell-spezifische URLs
            if self.config['model'].startswith('Shelly1'):
                url = f"http://{self.config['ip_address']}/relay/0"
                params = {'turn': 'on' if state else 'off'}
                
            elif self.config['model'].startswith('ShellyPlus'):
                url = f"http://{self.config['ip_address']}/rpc/Switch.Set"
                params = {'id': 0, 'on': state}
                
            else:
                self.logger.error(f"Unbekanntes Shelly-Modell: {self.config['model']}")
                return False
            
            response = requests.get(
                url,
                params=params,
                auth=(self.config.get('username'), self.config.get('password')),
                timeout=10
            )
            
            success = response.status_code == 200
            
            if success:
                self.logger.info(f"Shelly {'eingeschaltet' if state else 'ausgeschaltet'}")
            else:
                self.logger.error(f"Schaltfehler: HTTP {response.status_code}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Fehler beim Schalten: {e}")
            return False


class ShellyKompressorService:
    """Service für Kompressor-Steuerung über Shelly"""
    
    def __init__(self, app=None):
        self.app = app
        self.controller = None
        self.logger = logging.getLogger(__name__)
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask-App initialisieren"""
        self.app = app
        
        # Konfiguration laden
        config = app.config.get('SHELLY_CONFIG', {})
        
        if config.get('enabled', False):
            self.controller = ShellyController(config)
            self.logger.info("Shelly-Integration aktiviert")
        else:
            self.logger.info("Shelly-Integration deaktiviert")
    
    def kompressor_einschalten(self) -> Dict[str, Any]:
        """Kompressor über Shelly einschalten"""
        
        if not self.controller:
            return {
                'success': False,
                'error': 'Shelly-Integration nicht konfiguriert'
            }
        
        try:
            # Aktuellen Status prüfen
            status = self.controller.get_status()
            
            if not status or not status.get('online'):
                return {
                    'success': False,
                    'error': 'Shelly nicht erreichbar'
                }
            
            # Bereits eingeschaltet?
            if status.get('relay_on'):
                return {
                    'success': True,
                    'message': 'Kompressor war bereits eingeschaltet',
                    'status': status
                }
            
            # Einschalten
            success = self.controller.turn_on()
            
            if success:
                # Neuen Status abrufen
                new_status = self.controller.get_status()
                
                return {
                    'success': True,
                    'message': 'Kompressor erfolgreich eingeschaltet',
                    'status': new_status
                }
            else:
                return {
                    'success': False,
                    'error': 'Fehler beim Einschalten'
                }
                
        except Exception as e:
            self.logger.error(f"Fehler beim Einschalten: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def kompressor_ausschalten(self) -> Dict[str, Any]:
        """Kompressor über Shelly ausschalten"""
        
        if not self.controller:
            return {
                'success': False,
                'error': 'Shelly-Integration nicht konfiguriert'
            }
        
        try:
            # Einschalten-Logik analog, nur mit turn_off()
            status = self.controller.get_status()
            
            if not status or not status.get('online'):
                return {
                    'success': False,
                    'error': 'Shelly nicht erreichbar'
                }
            
            if not status.get('relay_on'):
                return {
                    'success': True,
                    'message': 'Kompressor war bereits ausgeschaltet',
                    'status': status
                }
            
            success = self.controller.turn_off()
            
            if success:
                new_status = self.controller.get_status()
                return {
                    'success': True,
                    'message': 'Kompressor erfolgreich ausgeschaltet',
                    'status': new_status
                }
            else:
                return {
                    'success': False,
                    'error': 'Fehler beim Ausschalten'
                }
                
        except Exception as e:
            self.logger.error(f"Fehler beim Ausschalten: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_kompressor_status(self) -> Dict[str, Any]:
        """Aktuellen Kompressor-Status abrufen"""
        
        if not self.controller:
            return {
                'online': False,
                'error': 'Shelly-Integration nicht konfiguriert'
            }
        
        return self.controller.get_status() or {
            'online': False,
            'error': 'Status nicht verfügbar'
        }


# Konfiguration-Template für Flask-App
SHELLY_CONFIG_TEMPLATE = {
    'enabled': False,  # Auf True setzen zum Aktivieren
    'ip_address': '192.168.1.100',  # Shelly IP-Adresse
    'model': 'Shelly1PM',  # Unterstützt: Shelly1, Shelly1PM, ShellyPlus1, ShellyPlus1PM
    'username': '',  # Optional: HTTP Auth Username
    'password': '',  # Optional: HTTP Auth Password
    'timeout': 10,   # Timeout in Sekunden
}

# Erstellt von Hans Hahn - Alle Rechte vorbehalten
