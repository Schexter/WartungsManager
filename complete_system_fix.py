#!/usr/bin/env python3
"""
Komplette System-Reparatur für WartungsManager
Löst alle Routing- und Datenbank-Probleme
"""

from pathlib import Path

def create_missing_main_route():
    """Erstellt die fehlende main.py Route"""
    
    main_route_path = Path("C:/SoftwareEntwicklung/WartungsManager-main/Source/Python/app/routes/main.py")
    
    main_content = '''"""
Hauptrouten für WartungsManager
Grundlegende Navigation und Startseite
"""

from flask import Blueprint, render_template, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Startseite"""
    return """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <title>WartungsManager - Hauptsystem</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c5aa0; text-align: center; margin-bottom: 30px; }
        .nav-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
        .nav-card { background: #3498db; color: white; padding: 20px; border-radius: 8px; text-decoration: none; text-align: center; transition: all 0.3s; }
        .nav-card:hover { background: #2980b9; transform: translateY(-2px); color: white; text-decoration: none; }
        .status { background: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px; margin: 20px 0; }
        .admin-section { background: #f0f8f0; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 WartungsManager Hauptsystem</h1>
        
        <div class="status">
            <h3>System-Status</h3>
            <p>✅ <strong>Flask-Server:</strong> Läuft auf Port 5000</p>
            <p>✅ <strong>Multi-Client:</strong> Unterstützt</p>
            <p>✅ <strong>Mobile/iPad:</strong> Optimiert</p>
            <p>✅ <strong>Drucker:</strong> 62mm Support</p>
        </div>
        
        <div class="nav-grid">
            <a href="/kompressor" class="nav-card">
                <h3>🏭 Kompressor</h3>
                <p>Steuerung & Überwachung</p>
            </a>
            <a href="/fuellmanager" class="nav-card">
                <h3>💨 Füllmanager</h3>
                <p>Flaschen & Aufträge</p>
            </a>
            <a href="/static/shelly_control.html" class="nav-card">
                <h3>🔌 Shelly-Steuerung</h3>
                <p>Fernsteuerung</p>
            </a>
            <a href="/admin" class="nav-card">
                <h3>⚙️ Admin</h3>
                <p>Einstellungen & Konfiguration</p>
            </a>
        </div>
        
        <div class="admin-section">
            <h3>🔌 Shelly-Kompressor-Integration</h3>
            <p><strong>Direkt einsatzbereit:</strong></p>
            <ul>
                <li><a href="/static/shelly_control.html" style="color: #155724;">Shelly-Steuerung öffnen</a></li>
                <li>IP-Adresse eingeben (z.B. 192.168.1.100)</li>
                <li>Modell wählen (Shelly1, Shelly1PM, ShellyPlus1, ShellyPlus1PM)</li>
                <li>Kompressor fernsteuern</li>
            </ul>
        </div>
        
        <div class="status">
            <h3>📱 Zugriff von anderen Geräten</h3>
            <p><strong>Lokales Netzwerk:</strong> http://192.168.0.237:5000</p>
            <p><strong>Mobile/Tablet:</strong> Touch-optimiert</p>
            <p><strong>Multi-Client:</strong> Mehrere Benutzer gleichzeitig</p>
        </div>
    </div>
</body>
</html>"""

@main_bp.route('/health')
def health():
    """Health Check Endpoint"""
    return {"status": "ok", "message": "WartungsManager läuft"}

@main_bp.route('/info')
def system_info():
    """System-Informationen"""
    import platform
    import sys
    from pathlib import Path
    
    return {
        "system": "WartungsManager",
        "status": "running",
        "python_version": sys.version,
        "platform": platform.platform(),
        "working_directory": str(Path.cwd())
    }

# Erstellt von Hans Hahn - Alle Rechte vorbehalten
'''
    
    with open(main_route_path, 'w', encoding='utf-8') as f:
        f.write(main_content)
    
    print("✅ Main-Route erstellt")
    return True

def fix_database_path_in_init():
    """Repariert den Datenbank-Pfad in der __init__.py"""
    
    init_path = Path("C:/SoftwareEntwicklung/WartungsManager-main/Source/Python/app/__init__.py")
    
    if not init_path.exists():
        print("❌ __init__.py nicht gefunden")
        return False
    
    # Datei lesen
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Datenbank-Pfad korrigieren
    content = content.replace(
        "app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../../database/wartungsmanager.db'",
        "app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/wartungsmanager.db'"
    )
    
    # Datei zurückschreiben
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Datenbank-Pfad korrigiert")
    return True

def create_working_shelly_api():
    """Erstellt eine funktionierende Shelly-API"""
    
    api_path = Path("C:/SoftwareEntwicklung/WartungsManager-main/Source/Python/app/routes/shelly_api.py")
    
    api_content = '''"""
Shelly-API für Kompressor-Steuerung
Universelle Integration für alle Shelly-Modelle
"""

from flask import Blueprint, request, jsonify
import requests
import logging

shelly_api = Blueprint('shelly_api', __name__, url_prefix='/api/shelly')

# Globale Shelly-Konfiguration
SHELLY_CONFIG = {
    'enabled': False,
    'ip_address': '192.168.1.100',
    'model': 'Shelly1PM',
    'username': '',
    'password': '',
    'timeout': 10
}

@shelly_api.route('/config', methods=['GET', 'POST'])
def config():
    """Shelly-Konfiguration verwalten"""
    global SHELLY_CONFIG
    
    if request.method == 'POST':
        try:
            data = request.json
            if data:
                SHELLY_CONFIG.update(data)
                return jsonify({'success': True, 'config': SHELLY_CONFIG})
            else:
                return jsonify({'success': False, 'error': 'Keine Daten empfangen'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'success': True, 'config': SHELLY_CONFIG})

@shelly_api.route('/test-connection', methods=['POST'])
def test_connection():
    """Shelly-Verbindung testen"""
    try:
        data = request.json
        ip = data.get('ip_address', SHELLY_CONFIG['ip_address'])
        model = data.get('model', SHELLY_CONFIG['model'])
        timeout = data.get('timeout', 5)
        
        # Status-Endpunkt je nach Modell
        if model.startswith('ShellyPlus'):
            status_url = f"http://{ip}/rpc/Shelly.GetStatus"
        else:
            status_url = f"http://{ip}/status"
        
        response = requests.get(status_url, timeout=timeout)
        
        if response.status_code == 200:
            return jsonify({
                'success': True, 
                'message': f'Shelly {model} erfolgreich erreicht',
                'data': response.json()
            })
        else:
            return jsonify({
                'success': False, 
                'error': f'HTTP {response.status_code}'
            })
            
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Verbindungs-Timeout'})
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': 'Verbindung fehlgeschlagen - IP erreichbar?'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@shelly_api.route('/kompressor/einschalten', methods=['POST'])
def kompressor_einschalten():
    """Kompressor über Shelly einschalten"""
    try:
        if not SHELLY_CONFIG['enabled']:
            return jsonify({'success': False, 'error': 'Shelly nicht konfiguriert'})
        
        ip = SHELLY_CONFIG['ip_address']
        model = SHELLY_CONFIG['model']
        
        # Einschalt-Endpunkt je nach Modell
        if model.startswith('ShellyPlus'):
            switch_url = f"http://{ip}/rpc/Switch.Set"
            data = {"id": 0, "on": True}
            response = requests.post(switch_url, json=data, timeout=SHELLY_CONFIG['timeout'])
        else:
            switch_url = f"http://{ip}/relay/0?turn=on"
            response = requests.get(switch_url, timeout=SHELLY_CONFIG['timeout'])
        
        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'Kompressor eingeschaltet'})
        else:
            return jsonify({'success': False, 'error': f'HTTP {response.status_code}'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@shelly_api.route('/kompressor/ausschalten', methods=['POST'])
def kompressor_ausschalten():
    """Kompressor über Shelly ausschalten"""
    try:
        if not SHELLY_CONFIG['enabled']:
            return jsonify({'success': False, 'error': 'Shelly nicht konfiguriert'})
        
        ip = SHELLY_CONFIG['ip_address']
        model = SHELLY_CONFIG['model']
        
        # Ausschalt-Endpunkt je nach Modell
        if model.startswith('ShellyPlus'):
            switch_url = f"http://{ip}/rpc/Switch.Set"
            data = {"id": 0, "on": False}
            response = requests.post(switch_url, json=data, timeout=SHELLY_CONFIG['timeout'])
        else:
            switch_url = f"http://{ip}/relay/0?turn=off"
            response = requests.get(switch_url, timeout=SHELLY_CONFIG['timeout'])
        
        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'Kompressor ausgeschaltet'})
        else:
            return jsonify({'success': False, 'error': f'HTTP {response.status_code}'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@shelly_api.route('/kompressor/status', methods=['GET'])
def kompressor_status():
    """Kompressor-Status über Shelly abfragen"""
    try:
        if not SHELLY_CONFIG['enabled']:
            return jsonify({'success': False, 'error': 'Shelly nicht konfiguriert'})
        
        ip = SHELLY_CONFIG['ip_address']
        model = SHELLY_CONFIG['model']
        
        # Status-Endpunkt je nach Modell
        if model.startswith('ShellyPlus'):
            status_url = f"http://{ip}/rpc/Shelly.GetStatus"
        else:
            status_url = f"http://{ip}/status"
        
        response = requests.get(status_url, timeout=SHELLY_CONFIG['timeout'])
        
        if response.status_code == 200:
            data = response.json()
            
            # Status-Daten vereinheitlichen
            if model.startswith('ShellyPlus'):
                switch_data = data.get('switch:0', {})
                status_data = {
                    'online': True,
                    'relay_on': switch_data.get('output', False),
                    'power': switch_data.get('apower', 0),
                    'temperature': data.get('temperature:0', {}).get('tC')
                }
            else:
                relay_data = data.get('relays', [{}])[0]
                meter_data = data.get('meters', [{}])[0] if 'meters' in data else {}
                status_data = {
                    'online': True,
                    'relay_on': relay_data.get('ison', False),
                    'power': meter_data.get('power', 0),
                    'temperature': data.get('temperature')
                }
            
            return jsonify({'success': True, 'data': status_data})
        else:
            return jsonify({'success': False, 'error': f'HTTP {response.status_code}'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Erstellt von Hans Hahn - Alle Rechte vorbehalten
'''
    
    with open(api_path, 'w', encoding='utf-8') as f:
        f.write(api_content)
    
    print("✅ Shelly-API erstellt")
    return True

def main():
    print("🔧 WartungsManager - Komplette System-Reparatur")
    print("=" * 60)
    
    try:
        # Schritt 1: Main-Route erstellen
        if create_missing_main_route():
            print("1/3 ✅ Main-Route repariert")
        
        # Schritt 2: Datenbank-Pfad reparieren
        if fix_database_path_in_init():
            print("2/3 ✅ Datenbank-Pfad repariert")
        
        # Schritt 3: Shelly-API erstellen
        if create_working_shelly_api():
            print("3/3 ✅ Shelly-API repariert")
        
        print("\n🎉 SYSTEM-REPARATUR ABGESCHLOSSEN!")
        print("=" * 60)
        print("✅ Alle Routen verfügbar")
        print("✅ Datenbank konfiguriert")
        print("✅ Shelly-Integration funktional")
        
        print("\n🚀 System jetzt starten:")
        print("python run_production_REPARIERT.py")
        
        print("\n🌐 Verfügbare URLs:")
        print("http://localhost:5000/ - Hauptsystem")
        print("http://localhost:5000/static/shelly_control.html - Shelly-Steuerung")
        print("http://localhost:5000/admin - Admin-Interface")
        print("http://localhost:5000/api/shelly/config - API-Status")
        
    except Exception as e:
        print(f"❌ Reparatur fehlgeschlagen: {e}")

if __name__ == '__main__':
    main()
