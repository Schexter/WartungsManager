"""
WartungsManager - Shelly Network Discovery & Management
Automatische Erkennung aller Shelly-Geräte im Netzwerk
"""

import os
import sys
import json
import time
import socket
import requests
import threading
from typing import List, Dict, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict

@dataclass
class ShellyDevice:
    """Shelly-Gerät Datenklasse"""
    ip: str
    mac: str = ""
    name: str = ""
    model: str = ""
    gen: int = 1  # Generation 1 oder 2
    fw_version: str = ""
    relay_count: int = 1
    has_power_meter: bool = False
    online: bool = True
    role: str = ""  # "kompressor", "widget", etc.
    custom_name: str = ""  # Benutzerdefinierter Name
    
    def to_dict(self):
        return asdict(self)

class ShellyDiscovery:
    """Shelly Netzwerk-Scanner"""
    
    def __init__(self, subnet="192.168.0"):
        self.subnet = subnet
        self.devices = []
        self.timeout = 0.5
        
    def scan_ip(self, ip: str) -> ShellyDevice:
        """Prüfe eine IP auf Shelly-Gerät"""
        try:
            # Shelly Gen1 Check
            response = requests.get(f"http://{ip}/shelly", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                
                # Status-Details holen
                status = requests.get(f"http://{ip}/status", timeout=self.timeout).json()
                
                device = ShellyDevice(
                    ip=ip,
                    mac=data.get('mac', ''),
                    name=status.get('device', {}).get('hostname', ''),
                    model=data.get('type', ''),
                    gen=1,
                    fw_version=data.get('fw', ''),
                    relay_count=len(status.get('relays', [1])),
                    has_power_meter='meters' in status
                )
                
                return device
        except:
            pass
            
        try:
            # Shelly Gen2 (Plus) Check
            response = requests.post(
                f"http://{ip}/rpc",
                json={"id": 1, "method": "Shelly.GetDeviceInfo"},
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json().get('result', {})
                
                # Status holen
                status_resp = requests.post(
                    f"http://{ip}/rpc",
                    json={"id": 1, "method": "Shelly.GetStatus"},
                    timeout=self.timeout
                )
                status = status_resp.json().get('result', {})
                
                # Switch-Anzahl ermitteln
                switch_count = 0
                for key in status.keys():
                    if key.startswith('switch:'):
                        switch_count += 1
                
                device = ShellyDevice(
                    ip=ip,
                    mac=data.get('mac', ''),
                    name=data.get('name', ''),
                    model=data.get('model', ''),
                    gen=2,
                    fw_version=data.get('fw_id', ''),
                    relay_count=switch_count or 1,
                    has_power_meter='switch:0' in status and 'apower' in status.get('switch:0', {})
                )
                
                return device
        except:
            pass
            
        return None
    
    def scan_network(self, ip_range=(1, 254)):
        """Scanne das gesamte Netzwerk"""
        print(f"\n🔍 Scanne Netzwerk {self.subnet}.x ...")
        print(f"   IP-Bereich: {self.subnet}.{ip_range[0]} - {self.subnet}.{ip_range[1]}")
        
        found_devices = []
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            
            for i in range(ip_range[0], ip_range[1] + 1):
                ip = f"{self.subnet}.{i}"
                futures.append(executor.submit(self.scan_ip, ip))
            
            # Progress-Bar
            completed = 0
            total = len(futures)
            
            for future in as_completed(futures):
                completed += 1
                print(f"\r   Fortschritt: {completed}/{total} IPs gescannt", end="")
                
                device = future.result()
                if device:
                    found_devices.append(device)
                    print(f"\n   ✅ Gefunden: {device.model} auf {device.ip}")
        
        print(f"\n\n📊 Scan abgeschlossen: {len(found_devices)} Shelly-Geräte gefunden")
        self.devices = found_devices
        return found_devices

class ShellyManager:
    """Shelly-Verwaltung und Konfiguration"""
    
    CONFIG_FILE = Path(__file__).parent / "shelly_devices.json"
    
    def __init__(self):
        self.devices = []
        self.load_config()
    
    def load_config(self):
        """Lade gespeicherte Geräte-Konfiguration"""
        if self.CONFIG_FILE.exists():
            with open(self.CONFIG_FILE, 'r') as f:
                data = json.load(f)
                self.devices = [ShellyDevice(**d) for d in data]
    
    def save_config(self):
        """Speichere Geräte-Konfiguration"""
        data = [d.to_dict() for d in self.devices]
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Konfiguration gespeichert in: {self.CONFIG_FILE}")
    
    def add_device(self, device: ShellyDevice):
        """Füge Gerät hinzu oder aktualisiere"""
        # Prüfe ob schon vorhanden
        for i, d in enumerate(self.devices):
            if d.ip == device.ip:
                self.devices[i] = device
                return
        self.devices.append(device)
    
    def get_kompressor_device(self):
        """Hole das als Kompressor markierte Gerät"""
        for device in self.devices:
            if device.role == "kompressor":
                return device
        return None
    
    def get_widget_devices(self):
        """Hole alle Widget-Geräte"""
        return [d for d in self.devices if d.role == "widget"]
    
    def switch_device(self, ip: str, on: bool = True, relay: int = 0):
        """Schalte ein Gerät"""
        device = next((d for d in self.devices if d.ip == ip), None)
        if not device:
            return {"success": False, "error": "Gerät nicht gefunden"}
        
        try:
            if device.gen == 2:
                # Shelly Gen2
                response = requests.post(
                    f"http://{ip}/rpc",
                    json={"id": 1, "method": "Switch.Set", "params": {"id": relay, "on": on}},
                    timeout=5
                )
            else:
                # Shelly Gen1
                action = "on" if on else "off"
                response = requests.get(
                    f"http://{ip}/relay/{relay}?turn={action}",
                    timeout=5
                )
            
            if response.status_code == 200:
                return {"success": True, "message": f"Gerät {'eingeschaltet' if on else 'ausgeschaltet'}"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_device_status(self, ip: str):
        """Hole aktuellen Status eines Geräts"""
        device = next((d for d in self.devices if d.ip == ip), None)
        if not device:
            return None
        
        try:
            if device.gen == 2:
                response = requests.post(
                    f"http://{ip}/rpc",
                    json={"id": 1, "method": "Shelly.GetStatus"},
                    timeout=5
                )
                if response.status_code == 200:
                    return response.json().get('result', {})
            else:
                response = requests.get(f"http://{ip}/status", timeout=5)
                if response.status_code == 200:
                    return response.json()
        except:
            pass
        
        return None

def interactive_setup():
    """Interaktives Setup mit Netzwerk-Scan"""
    print("\n" + "="*60)
    print("     WartungsManager - Shelly Auto-Discovery")
    print("="*60)
    
    # Netzwerk bestimmen
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    subnet = '.'.join(local_ip.split('.')[:-1])
    
    print(f"\n📡 Ihr Netzwerk: {subnet}.0/24")
    print(f"   Lokale IP: {local_ip}")
    
    custom = input("\nAnderes Subnetz scannen? (Enter für Standard): ").strip()
    if custom:
        subnet = custom
    
    # Scanner initialisieren
    discovery = ShellyDiscovery(subnet)
    
    # Scan durchführen
    devices = discovery.scan_network()
    
    if not devices:
        print("\n❌ Keine Shelly-Geräte gefunden!")
        print("   Tipps:")
        print("   - Sind die Shellys im gleichen Netzwerk?")
        print("   - Ist die IP-Range korrekt?")
        print("   - Firewall blockiert vielleicht?")
        return
    
    # Manager initialisieren
    manager = ShellyManager()
    
    # Geräte anzeigen
    print("\n" + "="*60)
    print("     Gefundene Shelly-Geräte")
    print("="*60)
    
    for i, device in enumerate(devices, 1):
        print(f"\n[{i}] {device.model} - {device.ip}")
        print(f"    MAC: {device.mac}")
        print(f"    Name: {device.name or '(nicht gesetzt)'}")
        print(f"    Generation: {device.gen}")
        print(f"    Relais: {device.relay_count}")
        print(f"    Leistungsmessung: {'✅' if device.has_power_meter else '❌'}")
    
    # Kompressor-Gerät wählen
    print("\n" + "="*60)
    print("     Kompressor-Steuerung konfigurieren")
    print("="*60)
    
    while True:
        choice = input("\nWelches Gerät soll den KOMPRESSOR steuern? (Nummer): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(devices):
                kompressor = devices[idx]
                kompressor.role = "kompressor"
                
                # Custom Name
                name = input(f"Name für Kompressor-Steuerung [{kompressor.model}]: ").strip()
                kompressor.custom_name = name or f"Kompressor {kompressor.model}"
                
                manager.add_device(kompressor)
                print(f"✅ {kompressor.custom_name} als Kompressor-Steuerung konfiguriert")
                break
        except:
            print("❌ Ungültige Eingabe")
    
    # Widget-Geräte wählen
    print("\n" + "="*60)
    print("     Dashboard-Widgets konfigurieren")
    print("="*60)
    print("Wählen Sie weitere Geräte als Dashboard-Widgets")
    print("(Enter ohne Eingabe zum Überspringen)")
    
    remaining = [d for d in devices if d.role != "kompressor"]
    
    for device in remaining:
        print(f"\n📱 {device.model} - {device.ip}")
        add = input("Als Widget hinzufügen? (j/n): ").lower()
        
        if add in ['j', 'ja', 'yes']:
            device.role = "widget"
            
            # Custom Name
            name = input(f"Anzeigename im Dashboard: ").strip()
            device.custom_name = name or device.model
            
            manager.add_device(device)
            print(f"✅ {device.custom_name} als Widget hinzugefügt")
    
    # Speichern
    manager.save_config()
    
    # Test
    print("\n" + "="*60)
    print("     Konfiguration abgeschlossen")
    print("="*60)
    
    print("\n📋 Zusammenfassung:")
    print(f"   Kompressor: {manager.get_kompressor_device().custom_name}")
    
    widgets = manager.get_widget_devices()
    if widgets:
        print(f"   Widgets: {len(widgets)}")
        for w in widgets:
            print(f"      - {w.custom_name}")
    
    # Schalttest
    test = input("\n⚡ Schalttest durchführen? (j/n): ").lower()
    if test in ['j', 'ja']:
        device = manager.get_kompressor_device()
        print(f"\nTeste {device.custom_name}...")
        
        # AN
        print("   Schalte AN...")
        result = manager.switch_device(device.ip, True)
        print(f"   {result}")
        
        time.sleep(2)
        
        # AUS
        print("   Schalte AUS...")
        result = manager.switch_device(device.ip, False)
        print(f"   {result}")
    
    print("\n✅ Setup abgeschlossen!")
    print("\n⚠️ WICHTIG: Server neu starten für Änderungen:")
    print("   python run_production.py")

def list_devices():
    """Zeige alle konfigurierten Geräte"""
    manager = ShellyManager()
    
    if not manager.devices:
        print("❌ Keine Geräte konfiguriert")
        print("   Führen Sie 'python shelly_discovery.py' aus")
        return
    
    print("\n📋 Konfigurierte Shelly-Geräte:")
    
    kompressor = manager.get_kompressor_device()
    if kompressor:
        print(f"\n⚙️ KOMPRESSOR-STEUERUNG:")
        print(f"   {kompressor.custom_name}")
        print(f"   IP: {kompressor.ip}")
        print(f"   Modell: {kompressor.model}")
    
    widgets = manager.get_widget_devices()
    if widgets:
        print(f"\n📱 DASHBOARD-WIDGETS:")
        for w in widgets:
            print(f"   • {w.custom_name}")
            print(f"     IP: {w.ip}, Modell: {w.model}")

def test_all():
    """Teste alle konfigurierten Geräte"""
    manager = ShellyManager()
    
    print("\n🧪 Teste alle Geräte...")
    
    for device in manager.devices:
        print(f"\n{device.custom_name} ({device.ip}):")
        status = manager.get_device_status(device.ip)
        
        if status:
            print(f"   ✅ Online")
            
            # Status-Details
            if device.gen == 2:
                switch = status.get('switch:0', {})
                print(f"   Relais: {'AN' if switch.get('output') else 'AUS'}")
                if 'apower' in switch:
                    print(f"   Leistung: {switch['apower']} W")
            else:
                relay = status.get('relays', [{}])[0]
                print(f"   Relais: {'AN' if relay.get('ison') else 'AUS'}")
                if 'meters' in status:
                    print(f"   Leistung: {status['meters'][0].get('power', 0)} W")
        else:
            print(f"   ❌ Offline oder nicht erreichbar")

def main():
    """Hauptprogramm"""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'list':
            list_devices()
        elif sys.argv[1] == 'test':
            test_all()
        elif sys.argv[1] == 'scan':
            interactive_setup()
        else:
            print("Verwendung:")
            print("  python shelly_discovery.py       # Interaktives Setup")
            print("  python shelly_discovery.py scan  # Neu scannen")
            print("  python shelly_discovery.py list  # Geräte anzeigen")
            print("  python shelly_discovery.py test  # Alle testen")
    else:
        # Check ob schon konfiguriert
        manager = ShellyManager()
        if manager.devices:
            print("\n✅ Shelly-Geräte bereits konfiguriert!")
            list_devices()
            print("\n🔄 Zum Neu-Scannen: python shelly_discovery.py scan")
        else:
            interactive_setup()

if __name__ == "__main__":
    main()

# Erstellt von Hans Hahn - Alle Rechte vorbehalten
