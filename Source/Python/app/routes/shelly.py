"""
Shelly IoT Integration für WartungsManager
Netzwerk-Discovery und Gerätesteuerung
"""

from flask import Blueprint, jsonify, request, render_template
import socket
import subprocess
import platform
import json
import requests
import ipaddress
import concurrent.futures
from datetime import datetime
import os

shelly_bp = Blueprint('shelly', __name__, url_prefix='/shelly')

# Dashboard Route
@shelly_bp.route('/')
def shelly_main():
    """Zeige Shelly-Scanner Hauptseite"""
    return render_template('shelly.html')

@shelly_bp.route('/dashboard')
def shelly_dashboard():
    """Zeige Shelly-Dashboard für konfigurierte Geräte"""
    return render_template('shelly_dashboard.html')

# Konfigurations-Seite
@shelly_bp.route('/config')
def config_page():
    """Zeige Konfigurations-Seite"""
    return render_template('shelly_config.html')

# Einfache Konfigurations-Seite
@shelly_bp.route('/simple-config')
def simple_config_page():
    """Zeige einfache Konfigurations-Seite"""
    return render_template('shelly_simple_config.html')

# Optionale Konfiguration laden
CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 
    'config', 
    'shelly_config.json'
)

def load_config():
    """Lade optionale Konfiguration"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f).get('shelly_config', {})
    except:
        pass
    return {}

def get_local_ip():
    """Ermittelt die lokale IP-Adresse des Systems"""
    try:
        # Verbinde zu Google DNS um lokale IP zu finden
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "192.168.0.1"

def get_network_range():
    """Ermittelt den Netzwerkbereich basierend auf der lokalen IP"""
    try:
        local_ip = get_local_ip()
        # Extrahiere Netzwerk-Prefix (z.B. 192.168.0 aus 192.168.0.238)
        parts = local_ip.split('.')
        if len(parts) >= 3:
            return '.'.join(parts[:3])
        return "192.168.0"
    except Exception:
        return "192.168.0"

@shelly_bp.route('/api/network-detect')
def detect_network():
    """Automatische Netzwerkerkennung"""
    try:
        network_range = get_network_range()
        local_ip = get_local_ip()
        
        return jsonify({
            'success': True,
            'network_range': network_range,
            'local_ip': local_ip,
            'subnet': f"{network_range}.0/24",
            'message': f'Netzwerk erkannt: {network_range}.0/24'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback': '192.168.0'
        })

def check_shelly_device(ip, timeout=1):
    """Prüft ob eine IP-Adresse ein Shelly-Gerät ist"""
    device_info = None
    
    # Alle Shelly-Endpoints für verschiedene Generationen
    shelly_endpoints = [
        # Gen 2 / Plus Endpoints
        ('/rpc/Shelly.GetDeviceInfo', 2, 'Plus/Pro'),
        ('/rpc/Shelly.GetInfo', 2, 'Plus'),
        ('/rpc/Shelly.GetStatus', 2, 'Plus'),
        ('/rpc/Sys.GetStatus', 2, 'Plus'),
        # Gen 1 Endpoints
        ('/shelly', 1, 'Gen1'),
        ('/status', 1, 'Gen1'),
        ('/settings', 1, 'Gen1'),
        ('/device/status', 1, 'Gen1'),
    ]
    
    for endpoint, gen, device_type in shelly_endpoints:
        try:
            # Versuche verschiedene Ports (80 und 8080)
            for port in [80, 8080]:
                url = f'http://{ip}:{port}{endpoint}'
                try:
                    response = requests.get(
                        url,
                        timeout=timeout,
                        headers={'Accept': 'application/json'}
                    )
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                        except:
                            # Manchmal kommt HTML zurück
                            continue
                            
                        # Parse Device Info basierend auf Generation
                        if gen == 2:
                            # Hole verschiedene Name-Felder für Gen 2
                            device_name = (
                                data.get('name') or 
                                data.get('id') or 
                                data.get('device', {}).get('name') or
                                data.get('device', {}).get('hostname') or
                                f'Shelly-{ip.split(".")[-1]}'
                            )
                            # Wenn Name immer noch None ist, verwende Modell + IP
                            if device_name in ['None', None, '']:
                                model_name = data.get('model', 'Shelly')
                                device_name = f'{model_name}-{ip.split(".")[-1]}'
                            
                            device_info = {
                                'ip': ip,
                                'port': port,
                                'name': device_name,
                                'model': data.get('model', data.get('app', 'Shelly Plus')),
                                'mac': data.get('mac', data.get('device', {}).get('mac', 'Unknown')),
                                'gen': 2,
                                'online': True,
                                'type': f'Shelly {device_type}',
                                'endpoint': endpoint,
                                'firmware': data.get('ver', data.get('fw', 'Unknown'))
                            }
                        else:
                            # Hole verschiedene Name-Felder für Gen 1
                            device_name = (
                                data.get('name') or 
                                data.get('device', {}).get('hostname') or
                                data.get('device', {}).get('name') or
                                data.get('hostname') or
                                f'Shelly-{ip.split(".")[-1]}'
                            )
                            # Wenn Name immer noch None ist, verwende Type + IP
                            if device_name in ['None', None, '']:
                                type_name = data.get('type', 'Shelly')
                                device_name = f'{type_name}-{ip.split(".")[-1]}'
                                
                            device_info = {
                                'ip': ip,
                                'port': port,
                                'name': device_name,
                                'model': data.get('type', data.get('device', {}).get('type', 'Shelly Gen1')),
                                'mac': data.get('mac', data.get('device', {}).get('mac', 'Unknown')),
                                'gen': 1,
                                'online': True,
                                'type': data.get('type', f'Shelly {device_type}'),
                                'endpoint': endpoint,
                                'firmware': data.get('fw_ver', data.get('fw', 'Unknown'))
                            }
                        
                        print(f"[SHELLY] ✓ Gefunden auf {ip}:{port}{endpoint} - {device_info['name']} ({device_info['model']})")
                        return device_info
                        
                except requests.exceptions.Timeout:
                    # Timeout ist normal für nicht-Shelly IPs
                    pass
                except requests.exceptions.ConnectionError:
                    # Verbindungsfehler ist normal für nicht-existierende IPs
                    pass
                except Exception as e:
                    # Debug nur bei unerwarteten Fehlern
                    if "json" not in str(e).lower():
                        print(f"[SHELLY] Unerwarteter Fehler bei {ip}:{port}{endpoint}: {str(e)}")
        except Exception as e:
            print(f"[SHELLY] Fehler beim Check von {ip}: {str(e)}")
    
    return None

@shelly_bp.route('/api/discover', methods=['POST'])
def discover_devices():
    """Netzwerk nach Shelly-Geräten durchsuchen"""
    try:
        data = request.get_json()
        config = load_config()
        
        # Nutze Konfiguration oder Defaults
        network = data.get('network', get_network_range())
        timeout = data.get('timeout', config.get('scan_timeout', 1))  # Reduziert auf 1 Sekunde
        workers = config.get('parallel_workers', 50)  # Erhöht für schnelleren Scan
        
        discovered = []
        scan_stats = {
            'total_ips': 254,
            'scanned': 0,
            'found': 0,
            'timeout': timeout,
            'workers': workers
        }
        
        print(f"[SHELLY] ========================================")
        print(f"[SHELLY] Starte Netzwerk-Scan")
        print(f"[SHELLY] Netzwerk: {network}.0/24")
        print(f"[SHELLY] Timeout: {timeout}s pro IP")
        print(f"[SHELLY] Worker-Threads: {workers}")
        print(f"[SHELLY] ========================================")
        
        # Optional: Prüfe bekannte Geräte aus Config zuerst
        if config.get('enabled', True):
            known_devices = config.get('known_devices', [])
            for device in known_devices:
                if device.get('enabled', False):
                    print(f"[SHELLY] Prüfe konfiguriertes Gerät: {device['ip']}")
                    result = check_shelly_device(device['ip'], timeout=timeout+1)
                    if result:
                        # Füge Config-Namen hinzu falls vorhanden
                        result['configured_name'] = device.get('name', result['name'])
                        discovered.append(result)
                        scan_stats['found'] += 1
        
        # IPs zum Scannen (1-254)
        ips_to_scan = [f"{network}.{i}" for i in range(1, 255)]
        
        print(f"[SHELLY] Scanne {len(ips_to_scan)} IP-Adressen...")
        
        # Parallel-Scan mit ThreadPool
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # Starte alle Scans
            future_to_ip = {
                executor.submit(check_shelly_device, ip, timeout): ip 
                for ip in ips_to_scan
            }
            
            # Sammle Ergebnisse mit Progress-Tracking
            for future in concurrent.futures.as_completed(future_to_ip):
                scan_stats['scanned'] += 1
                
                # Progress alle 25 IPs
                if scan_stats['scanned'] % 25 == 0:
                    print(f"[SHELLY] Progress: {scan_stats['scanned']}/254 IPs gescannt...")
                
                try:
                    result = future.result()
                    if result:
                        discovered.append(result)
                        scan_stats['found'] += 1
                        print(f"[SHELLY] ✓ Gerät #{scan_stats['found']} gefunden: {result['name']} ({result['ip']}) - {result['model']}")
                except Exception as e:
                    # Fehler ignorieren (normale Timeouts etc.)
                    pass
        
        print(f"[SHELLY] ========================================")
        print(f"[SHELLY] Scan abgeschlossen!")
        print(f"[SHELLY] IPs gescannt: {scan_stats['scanned']}")
        print(f"[SHELLY] Geräte gefunden: {scan_stats['found']}")
        
        # Falls keine echten Geräte gefunden
        if len(discovered) == 0:
            print(f"[SHELLY] ========================================")
            print(f"[SHELLY] KEINE Shelly-Geräte gefunden!")
            print(f"[SHELLY] Mögliche Ursachen:")
            print(f"[SHELLY] 1. Shellys sind in anderem Netzwerk-Segment")
            print(f"[SHELLY] 2. Shellys verwenden andere Ports (nicht 80/8080)")
            print(f"[SHELLY] 3. Firewall blockiert die Anfragen")
            print(f"[SHELLY] 4. Shellys sind ausgeschaltet/nicht erreichbar")
            print(f"[SHELLY] ")
            print(f"[SHELLY] Prüfen Sie bitte:")
            print(f"[SHELLY] - Sind die Shellys im Netzwerk {network}.x?")
            print(f"[SHELLY] - Können Sie http://<shelly-ip> im Browser aufrufen?")
            print(f"[SHELLY] ========================================")
        else:
            print(f"[SHELLY] ========================================")
            print(f"[SHELLY] Gefundene Geräte im Detail:")
            for i, device in enumerate(discovered, 1):
                print(f"[SHELLY] {i}. {device['name']}")
                print(f"[SHELLY]    - IP: {device['ip']}")
                if device.get('port') != 80:
                    print(f"[SHELLY]    - Port: {device.get('port', 80)}")
                print(f"[SHELLY]    - Model: {device['model']}")
                print(f"[SHELLY]    - MAC: {device.get('mac', 'Unknown')}")
                print(f"[SHELLY]    - Generation: {device.get('gen', '?')}")
                print(f"[SHELLY]    - Firmware: {device.get('firmware', 'Unknown')}")
            print(f"[SHELLY] ========================================")
        
        return jsonify({
            'status': 'success',
            'discovered': discovered,
            'count': len(discovered),
            'network_scanned': f'{network}.0/24',
            'stats': scan_stats
        })
        
    except Exception as e:
        print(f"[SHELLY] FEHLER beim Scan: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'discovered': []
        })

@shelly_bp.route('/api/scan')
def quick_scan():
    """Schneller Scan für bekannte Shelly-IPs"""
    try:
        network = get_network_range()
        
        # Bekannte Shelly-IPs (kann konfiguriert werden)
        known_ips = [
            f'{network}.100',
            f'{network}.101',
            f'{network}.102'
        ]
        
        devices = []
        for ip in known_ips:
            device = check_shelly_device(ip, timeout=1)
            if device:
                devices.append(device)
        
        # Demo-Gerät wenn nichts gefunden
        if len(devices) == 0:
            devices.append({
                'ip': f'{network}.100',
                'name': 'Shelly Demo Device',
                'model': 'Demo',
                'mac': 'Demo-MAC',
                'online': False,
                'type': 'Demo Device'
            })
        
        return jsonify({
            'status': 'success',
            'devices': devices,
            'found_count': len(devices)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@shelly_bp.route('/api/test/<ip>')
def test_device(ip):
    """Teste Verbindung zu einem Shelly-Gerät"""
    try:
        device = check_shelly_device(ip, timeout=2)
        
        if device:
            return jsonify({
                'success': True,
                'message': 'Gerät erreichbar',
                'device_info': device
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Gerät nicht erreichbar oder kein Shelly'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Fehler: {str(e)}'
        })

@shelly_bp.route('/api/device/<ip>/status')
def get_device_status(ip):
    """Detaillierten Status eines Shelly-Geräts abrufen"""
    try:
        print(f"[SHELLY] Rufe Status ab für {ip}")
        
        # Gen 2 API - Vollständiger Status
        try:
            # Versuche verschiedene Status-Endpoints
            endpoints = [
                '/rpc/Shelly.GetStatus',  # Vollständiger Status
                '/rpc/Switch.GetStatus?id=0',  # Switch-Status
                '/rpc/Sys.GetStatus',  # System-Status
            ]
            
            status_data = {}
            for endpoint in endpoints:
                url = f'http://{ip}{endpoint}'
                print(f"[SHELLY] Versuche: {url}")
                
                try:
                    response = requests.get(url, timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"[SHELLY] {endpoint}: {json.dumps(data, indent=2)}")
                        status_data[endpoint] = data
                except Exception as e:
                    print(f"[SHELLY] Fehler bei {endpoint}: {e}")
            
            # Extrahiere wichtige Infos
            result = {
                'ip': ip,
                'online': True,
                'raw_status': status_data
            }
            
            # Versuche Switch-Status zu extrahieren
            if '/rpc/Shelly.GetStatus' in status_data:
                full_status = status_data['/rpc/Shelly.GetStatus']
                if 'switch:0' in full_status:
                    switch_info = full_status['switch:0']
                    result['switch_on'] = switch_info.get('output', False)
                    result['power'] = switch_info.get('apower', 0)
                    result['voltage'] = switch_info.get('voltage', 0)
                    result['current'] = switch_info.get('current', 0)
                    result['temperature'] = switch_info.get('temperature', {}).get('tC', 0)
                    print(f"[SHELLY] Switch ist: {'EIN' if result['switch_on'] else 'AUS'}")
                    print(f"[SHELLY] Leistung: {result['power']}W")
            
            return jsonify(result)
            
        except Exception as e:
            print(f"[SHELLY] Gen2 Status-Fehler: {e}")
        
        # Gen 1 API Fallback
        try:
            url = f'http://{ip}/status'
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"[SHELLY] Gen1 Status: {json.dumps(data, indent=2)}")
                return jsonify({
                    'ip': ip,
                    'online': True,
                    'gen': 1,
                    'raw_status': data
                })
        except Exception as e:
            print(f"[SHELLY] Gen1 Status-Fehler: {e}")
        
        return jsonify({
            'ip': ip,
            'online': False,
            'error': 'Konnte Status nicht abrufen'
        })
        
    except Exception as e:
        print(f"[SHELLY] Status-Fehler für {ip}: {e}")
        return jsonify({'error': str(e)})

@shelly_bp.route('/api/toggle/<ip>', methods=['POST'])
def toggle_device(ip):
    """Shelly umschalten (Toggle)"""
    try:
        print(f"[SHELLY] Toggle Gerät {ip}")
        
        # Gen 2 API - Toggle-Befehl
        url = f'http://{ip}/rpc/Switch.Toggle'
        print(f"[SHELLY] Versuche Toggle: {url}")
        
        response = requests.post(
            url,
            json={'id': 0},
            timeout=3
        )
        
        print(f"[SHELLY] Toggle Response: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            was_on = result.get('was_on', False)
            print(f"[SHELLY] ✓ Toggle erfolgreich. War vorher: {'EIN' if was_on else 'AUS'}, ist jetzt: {'AUS' if was_on else 'EIN'}")
            return jsonify({
                'success': True,
                'was_on': was_on,
                'is_on': not was_on,
                'message': f'Gerät {ip} umgeschaltet'
            })
        
        return jsonify({'success': False, 'error': 'Toggle fehlgeschlagen'})
        
    except Exception as e:
        print(f"[SHELLY] Toggle-Fehler für {ip}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@shelly_bp.route('/api/device/<device_id>/on', methods=['POST'])
def switch_on(device_id):
    """Shelly einschalten - mit Workaround für Sync-Probleme"""
    try:
        ip = device_id
        print(f"[SHELLY] Schalte Gerät {ip} EIN")
        
        # WORKAROUND: Erst ausschalten, dann einschalten für Sync
        print(f"[SHELLY] Workaround: Erst OFF dann ON für sauberen Zustand")
        
        # Schritt 1: Ausschalten
        try:
            response = requests.post(
                f'http://{ip}/rpc/Switch.Set',
                json={'id': 0, 'on': False},
                timeout=2
            )
            print(f"[SHELLY] Schritt 1 (OFF): {response.text}")
        except Exception as e:
            print(f"[SHELLY] Schritt 1 Fehler: {e}")
        
        # Kurz warten
        import time
        time.sleep(0.5)
        
        # Schritt 2: Einschalten
        try:
            response = requests.post(
                f'http://{ip}/rpc/Switch.Set',
                json={'id': 0, 'on': True},
                timeout=2
            )
            print(f"[SHELLY] Schritt 2 (ON): Status {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"[SHELLY] ✓ Gerät {ip} sollte jetzt eingeschaltet sein")
                print(f"[SHELLY] Response: {result}")
                return jsonify({'success': True, 'message': f'Gerät {ip} eingeschaltet', 'response': result})
        except Exception as e:
            print(f"[SHELLY] Schritt 2 Fehler: {e}")
        
        return jsonify({'success': False, 'error': 'Schaltvorgang fehlgeschlagen'})
        
    except Exception as e:
        print(f"[SHELLY] Fehler beim Einschalten von {device_id}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@shelly_bp.route('/api/device/<device_id>/off', methods=['POST'])
def switch_off(device_id):
    """Shelly ausschalten"""
    try:
        # device_id IST die IP-Adresse
        ip = device_id
        print(f"[SHELLY] Schalte Gerät {ip} AUS")
        
        # Gen 2 API (Shelly Plus) - Versuche verschiedene IDs
        for switch_id in [0, 1]:  # Manche Geräte haben mehrere Switches
            try:
                url = f'http://{ip}/rpc/Switch.Set'
                payload = {'id': switch_id, 'on': False}
                print(f"[SHELLY] Versuche Gen2 API: {url} mit switch_id={switch_id}")
                
                response = requests.post(
                    url,
                    json=payload,
                    timeout=3
                )
                
                print(f"[SHELLY] Response Status: {response.status_code}")
                print(f"[SHELLY] Response Body: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    # Prüfe ob erfolgreich
                    if result.get('was_on') is not None:
                        print(f"[SHELLY] ✓ Gerät {ip} switch:{switch_id} erfolgreich ausgeschaltet")
                        print(f"[SHELLY] War vorher: {'EIN' if result.get('was_on') else 'AUS'}")
                        return jsonify({'success': True, 'message': f'Gerät {ip} ausgeschaltet', 'switch_id': switch_id})
                    elif 'error' in result:
                        print(f"[SHELLY] API Fehler: {result['error']}")
                        if switch_id == 0:
                            continue  # Versuche nächste ID
            except requests.exceptions.Timeout:
                print(f"[SHELLY] Gen2 API Timeout für {ip} switch:{switch_id}")
            except Exception as e:
                print(f"[SHELLY] Gen2 API Fehler für {ip} switch:{switch_id}: {e}")
        
        # Gen 1 API Fallback
        try:
            url = f'http://{ip}/relay/0?turn=off'
            print(f"[SHELLY] Versuche Gen1 API: {url}")
            response = requests.get(
                url,
                timeout=3
            )
            print(f"[SHELLY] Gen1 Response: {response.text}")
            
            if response.status_code == 200:
                print(f"[SHELLY] ✓ Gerät {ip} erfolgreich ausgeschaltet (Gen1)")
                return jsonify({'success': True, 'message': f'Gerät {ip} ausgeschaltet'})
        except requests.exceptions.Timeout:
            print(f"[SHELLY] Gen1 API Timeout für {ip}")
        except Exception as e:
            print(f"[SHELLY] Gen1 API Fehler für {ip}: {e}")
        
        print(f"[SHELLY] ✗ Gerät {ip} konnte nicht ausgeschaltet werden")
        return jsonify({'success': False, 'error': 'Gerät nicht erreichbar'})
        
    except Exception as e:
        print(f"[SHELLY] Fehler beim Ausschalten von {device_id}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@shelly_bp.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """Konfiguration lesen oder speichern"""
    try:
        from flask import current_app
        
        if request.method == 'GET':
            # Lade Konfiguration
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shelly_devices.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    devices = json.load(f)
                    return jsonify({
                        'success': True,
                        'devices': devices
                    })
            return jsonify({
                'success': True,
                'devices': []
            })
        
        else:  # POST
            # Speichere Konfiguration
            data = request.get_json()
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shelly_devices.json')
            
            with open(config_path, 'w') as f:
                json.dump(data.get('devices', []), f, indent=2)
            
            return jsonify({
                'success': True,
                'message': 'Konfiguration gespeichert',
                'devices': data.get('devices', [])
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@shelly_bp.route('/api/status')
def get_all_status():
    """Status aller konfigurierten Geräte"""
    try:
        # Für Demo: Statische Daten
        devices = [{
            'id': 'shelly1-demo',
            'name': 'Kompressor Hauptschalter',
            'type': 'Shelly Plus 1',
            'online': True,
            'relay_on': False,
            'power_w': 0,
            'temperature_c': 22.5,
            'ip': '192.168.0.100'
        }]
        
        return jsonify({
            'status': 'success',
            'data': {
                'devices': devices,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@shelly_bp.route('/api/kompressor/link', methods=['POST'])
def link_kompressor():
    """Verknüpfe Shelly mit Kompressor-Modul"""
    try:
        data = request.get_json()
        shelly_ip = data.get('ip')
        
        # Update Umgebungsvariable für Kompressor-Modul
        os.environ['SHELLY_KOMPRESSOR_IP'] = shelly_ip
        
        print(f"[SHELLY] Kompressor verknüpft mit Shelly {shelly_ip}")
        
        return jsonify({
            'success': True,
            'message': f'Shelly {shelly_ip} mit Kompressor verknüpft'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Erstellt von Hans Hahn - Alle Rechte vorbehalten