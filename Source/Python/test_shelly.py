#!/usr/bin/env python3
"""
Schnelltest für Shelly-Integration
"""

import sys
import requests
import json
from pathlib import Path

def test_basic_requirements():
    """Teste Basis-Anforderungen"""
    print("\n🔍 Teste Basis-Anforderungen...")
    
    # Python-Version
    print(f"   Python: {sys.version.split()[0]} ✅")
    
    # Requests
    try:
        import requests
        print(f"   Requests: {requests.__version__} ✅")
    except ImportError:
        print("   Requests: ❌ FEHLT! Installieren mit: pip install requests")
        return False
    
    # python-dotenv
    try:
        import dotenv
        print(f"   Python-dotenv: ✅")
    except ImportError:
        print("   Python-dotenv: ❌ FEHLT! Installieren mit: pip install python-dotenv")
        return False
    
    return True

def test_shelly_config():
    """Teste Shelly-Konfiguration"""
    print("\n📋 Teste Shelly-Konfiguration...")
    
    config_file = Path(__file__).parent / "shelly_devices.json"
    
    if not config_file.exists():
        print("   ❌ Keine Konfiguration gefunden!")
        print("      Führen Sie aus: python shelly_discovery.py")
        return False
    
    with open(config_file, 'r') as f:
        devices = json.load(f)
    
    print(f"   ✅ {len(devices)} Geräte konfiguriert")
    
    kompressor = next((d for d in devices if d['role'] == 'kompressor'), None)
    if kompressor:
        print(f"   ✅ Kompressor: {kompressor['custom_name']} ({kompressor['ip']})")
    else:
        print("   ⚠️  Kein Kompressor-Shelly zugewiesen")
    
    widgets = [d for d in devices if d['role'] == 'widget']
    if widgets:
        print(f"   ✅ Widgets: {len(widgets)} Geräte")
    
    return True

def test_shelly_connection():
    """Teste Verbindung zu Shellys"""
    print("\n🔌 Teste Shelly-Verbindungen...")
    
    config_file = Path(__file__).parent / "shelly_devices.json"
    if not config_file.exists():
        return False
    
    with open(config_file, 'r') as f:
        devices = json.load(f)
    
    online_count = 0
    offline_count = 0
    
    for device in devices:
        try:
            # Test-Request
            if device['gen'] == 2:
                url = f"http://{device['ip']}/rpc/Shelly.GetStatus"
                response = requests.post(url, json={"id": 1}, timeout=1)
            else:
                url = f"http://{device['ip']}/status"
                response = requests.get(url, timeout=1)
            
            if response.status_code == 200:
                print(f"   ✅ {device['custom_name']}: Online")
                online_count += 1
            else:
                print(f"   ❌ {device['custom_name']}: HTTP {response.status_code}")
                offline_count += 1
        except:
            print(f"   ❌ {device['custom_name']}: Offline")
            offline_count += 1
    
    print(f"\n   Zusammenfassung: {online_count} online, {offline_count} offline")
    return online_count > 0

def test_flask_integration():
    """Teste Flask-Integration"""
    print("\n🌐 Teste Flask-Integration...")
    
    try:
        # Teste ob Server läuft
        response = requests.get("http://localhost:5000/health", timeout=2)
        if response.status_code == 200:
            print("   ✅ WartungsManager läuft auf Port 5000")
            
            # Teste Shelly-Dashboard
            response = requests.get("http://localhost:5000/shelly/dashboard", timeout=2)
            if response.status_code == 200:
                print("   ✅ Shelly-Dashboard erreichbar")
            else:
                print("   ⚠️  Dashboard nicht erreichbar")
        else:
            print("   ❌ Server antwortet nicht korrekt")
    except:
        print("   ⚠️  Server läuft nicht")
        print("      Starten mit: python run_production.py")
    
    return True

def main():
    """Haupttest"""
    print("="*60)
    print("     WartungsManager - Shelly Integration Test")
    print("="*60)
    
    # Tests durchführen
    tests_passed = 0
    tests_total = 4
    
    if test_basic_requirements():
        tests_passed += 1
    
    if test_shelly_config():
        tests_passed += 1
    
    if test_shelly_connection():
        tests_passed += 1
    
    if test_flask_integration():
        tests_passed += 1
    
    # Ergebnis
    print("\n" + "="*60)
    print(f"     Testergebnis: {tests_passed}/{tests_total} Tests bestanden")
    print("="*60)
    
    if tests_passed == tests_total:
        print("\n✅ Alle Tests bestanden! System bereit.")
    elif tests_passed >= 2:
        print("\n⚠️  Einige Tests fehlgeschlagen. Grundfunktionen verfügbar.")
    else:
        print("\n❌ Kritische Tests fehlgeschlagen. Setup erforderlich!")
        print("\nNächste Schritte:")
        print("1. python shelly_discovery.py      # Shellys einrichten")
        print("2. python run_production.py        # Server starten")

if __name__ == "__main__":
    main()

# Erstellt von Hans Hahn - Alle Rechte vorbehalten
