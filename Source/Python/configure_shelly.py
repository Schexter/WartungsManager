"""
WartungsManager - Shelly Configuration Helper
Hilft bei der Einrichtung der Shelly-Integration
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv, set_key
import requests

# Pfade
BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR / '.env'

def print_header():
    """Zeige Header"""
    print("\n" + "="*60)
    print("     WartungsManager - Shelly-Integration Setup")
    print("="*60)
    print()

def load_current_config():
    """Lade aktuelle Konfiguration"""
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
    
    return {
        'enabled': os.getenv('SHELLY_ENABLED', 'false').lower() == 'true',
        'ip': os.getenv('SHELLY_IP', '192.168.0.100'),
        'model': os.getenv('SHELLY_MODEL', 'Shelly1PM'),
        'username': os.getenv('SHELLY_USERNAME', ''),
        'password': os.getenv('SHELLY_PASSWORD', ''),
        'timeout': int(os.getenv('SHELLY_TIMEOUT', '10'))
    }

def test_shelly_connection(ip, model, username='', password=''):
    """Teste Verbindung zu Shelly"""
    print(f"\n🔍 Teste Verbindung zu {ip}...")
    
    try:
        # URL je nach Modell
        if model.startswith('ShellyPlus'):
            url = f"http://{ip}/rpc/Shelly.GetStatus"
        else:
            url = f"http://{ip}/status"
        
        # Auth wenn vorhanden
        auth = None
        if username and password:
            auth = (username, password)
        
        response = requests.get(url, timeout=5, auth=auth)
        
        if response.status_code == 200:
            print(f"✅ Verbindung erfolgreich!")
            data = response.json()
            
            # Zeige einige Details
            if model.startswith('ShellyPlus'):
                switch = data.get('switch:0', {})
                print(f"   - Modell: {model}")
                print(f"   - Relais: {'AN' if switch.get('output') else 'AUS'}")
                if 'apower' in switch:
                    print(f"   - Leistung: {switch['apower']} W")
            else:
                relay = data.get('relays', [{}])[0]
                print(f"   - Modell: {model}")
                print(f"   - Relais: {'AN' if relay.get('ison') else 'AUS'}")
                if 'meters' in data:
                    print(f"   - Leistung: {data['meters'][0].get('power', 0)} W")
            
            return True
        else:
            print(f"❌ Fehler: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - Shelly nicht erreichbar")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Verbindungsfehler - IP-Adresse prüfen")
        return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def configure_shelly():
    """Interaktive Shelly-Konfiguration"""
    config = load_current_config()
    
    print("Aktuelle Konfiguration:")
    print(f"  - Status: {'✅ AKTIVIERT' if config['enabled'] else '❌ DEAKTIVIERT'}")
    print(f"  - IP-Adresse: {config['ip']}")
    print(f"  - Modell: {config['model']}")
    print(f"  - Username: {'***' if config['username'] else '(nicht gesetzt)'}")
    print(f"  - Password: {'***' if config['password'] else '(nicht gesetzt)'}")
    print()
    
    # Aktivierung
    activate = input("Shelly-Integration aktivieren? (j/n) [j]: ").lower()
    if activate in ['', 'j', 'ja', 'yes']:
        config['enabled'] = True
        
        # IP-Adresse
        print("\n📍 IP-Adresse des Shelly:")
        ip = input(f"IP-Adresse [{config['ip']}]: ").strip()
        if ip:
            config['ip'] = ip
        
        # Modell
        print("\n📦 Shelly-Modell:")
        print("  1. Shelly 1")
        print("  2. Shelly 1PM (mit Leistungsmessung)")
        print("  3. Shelly Plus 1")
        print("  4. Shelly Plus 1PM")
        model_choice = input("Auswahl [2]: ").strip()
        
        models = {
            '1': 'Shelly1',
            '2': 'Shelly1PM',
            '3': 'ShellyPlus1',
            '4': 'ShellyPlus1PM'
        }
        config['model'] = models.get(model_choice, 'Shelly1PM')
        
        # Authentifizierung (optional)
        print("\n🔐 Authentifizierung (optional):")
        username = input(f"Username [{config['username'] or 'leer'}]: ").strip()
        if username:
            config['username'] = username
            
            password = input("Password: ").strip()
            if password:
                config['password'] = password
        
        # Verbindung testen
        if test_shelly_connection(config['ip'], config['model'], 
                                 config['username'], config['password']):
            
            # Speichern
            save = input("\n💾 Konfiguration speichern? (j/n) [j]: ").lower()
            if save in ['', 'j', 'ja', 'yes']:
                save_config(config)
                print("✅ Konfiguration gespeichert!")
                
                print("\n⚠️ WICHTIG: Server neu starten damit Änderungen wirksam werden!")
                print("   Befehl: python run_production.py")
        else:
            print("\n⚠️ Verbindung fehlgeschlagen - Konfiguration prüfen!")
    else:
        # Deaktivieren
        config['enabled'] = False
        save_config(config)
        print("✅ Shelly-Integration deaktiviert")

def save_config(config):
    """Speichere Konfiguration in .env"""
    set_key(ENV_FILE, 'SHELLY_ENABLED', 'true' if config['enabled'] else 'false')
    set_key(ENV_FILE, 'SHELLY_IP', config['ip'])
    set_key(ENV_FILE, 'SHELLY_MODEL', config['model'])
    set_key(ENV_FILE, 'SHELLY_USERNAME', config['username'])
    set_key(ENV_FILE, 'SHELLY_PASSWORD', config['password'])
    set_key(ENV_FILE, 'SHELLY_TIMEOUT', str(config.get('timeout', 10)))

def test_mode():
    """Schnelltest der aktuellen Konfiguration"""
    config = load_current_config()
    
    if not config['enabled']:
        print("❌ Shelly-Integration ist deaktiviert!")
        print("   Führen Sie 'python configure_shelly.py' aus zum Aktivieren")
        return
    
    print(f"Teste {config['model']} auf {config['ip']}...")
    
    if test_shelly_connection(config['ip'], config['model'], 
                             config['username'], config['password']):
        print("\n✅ Shelly ist bereit!")
        
        # Schalttest
        test_switch = input("\nSchalttest durchführen? (j/n): ").lower()
        if test_switch in ['j', 'ja']:
            print("⚡ Schalte Relais AN...")
            # Hier würde der echte Schaltbefehl kommen
            print("   (Simulation - im echten Betrieb würde jetzt geschaltet)")
    else:
        print("\n❌ Shelly nicht erreichbar - Konfiguration prüfen!")

def main():
    """Hauptprogramm"""
    print_header()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_mode()
    else:
        configure_shelly()
    
    print("\n" + "="*60)

if __name__ == "__main__":
    # Installiere python-dotenv falls nicht vorhanden
    try:
        from dotenv import load_dotenv, set_key
    except ImportError:
        print("Installiere python-dotenv...")
        os.system("pip install python-dotenv")
        from dotenv import load_dotenv, set_key
    
    # Installiere requests falls nicht vorhanden
    try:
        import requests
    except ImportError:
        print("Installiere requests...")
        os.system("pip install requests")
        import requests
    
    main()

# Erstellt von Hans Hahn - Alle Rechte vorbehalten
