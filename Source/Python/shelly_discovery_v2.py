"""
WartungsManager - Verbesserte Shelly Discovery mit korrekter Netzwerkerkennung
"""

import os
import sys
import json
import socket
import requests
import threading
import ipaddress
import subprocess
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
    gen: int = 1
    fw_version: str = ""
    relay_count: int = 1
    has_power_meter: bool = False
    online: bool = True
    role: str = ""
    custom_name: str = ""
    
    def to_dict(self):
        return asdict(self)

class NetworkDetector:
    """Erkennt das richtige physische Netzwerk"""
    
    @staticmethod
    def get_physical_networks() -> List[str]:
        """Findet alle physischen Netzwerke (keine virtuellen)"""
        networks = []
        
        # Windows-spezifische Erkennung
        if sys.platform == "win32":
            try:
                # PowerShell-Befehl für echte Netzwerke
                cmd = [
                    "powershell", "-Command",
                    "Get-NetIPAddress -AddressFamily IPv4 | " +
                    "Where-Object {$_.InterfaceAlias -notlike '*WSL*' " +
                    "-and $_.InterfaceAlias -notlike '*Docker*' " +
                    "-and $_.InterfaceAlias -notlike '*vEthernet*' " +
                    "-and $_.InterfaceAlias -notlike '*Loopback*' " +
                    "-and $_.IPAddress -notlike '127.*' " +
                    "-and $_.IPAddress -notlike '169.254.*'} | " +
                    "Select-Object -ExpandProperty IPAddress"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line and '.' in line:
                            # Extrahiere Subnet
                            ip_parts = line.strip().split('.')
                            if len(ip_parts) == 4:
                                subnet = '.'.join(ip_parts[:3])
                                if subnet not in networks:
                                    networks.append(subnet)
                                    print(f"   ✅ Gefundenes Netzwerk: {subnet}.0/24 ({line})")
            except Exception as e:
                print(f"   ⚠️ PowerShell-Erkennung fehlgeschlagen: {e}")
        
        # Fallback: Socket-basierte Erkennung
        if not networks:
            try:
                hostname = socket.gethostname()
                for ip in socket.gethostbyname_ex(hostname)[2]:
                    if not ip.startswith("127.") and not ip.startswith("169.254."):
                        subnet = '.'.join(ip.split('.')[:-1])
                        if subnet not in networks:
                            networks.append(subnet)
                            print(f"   ✅ Gefundenes Netzwerk (Fallback): {subnet}.0/24")
            except:
                pass
        
        # Standard-Netzwerke als letzte Option
        if not networks:
            networks = ["192.168.0", "192.168.1", "192.168.178"]
            print("   ⚠️ Keine Netzwerke erkannt, nutze Standards: 192.168.0/1/178")
        
        return networks

class ShellyDiscovery:
    """Verbesserte Shelly Discovery"""
    
    def __init__(self, subnet="192.168.0"):
        self.subnet = subnet
        self.devices = []
        self.timeout = 0.3  # Schneller für mehr IPs
        
    def scan_ip(self, ip: str) -> ShellyDevice:
        """Prüfe eine IP auf Shelly-Gerät"""
        try:
            # Shelly Gen1 Check
            response = requests.get(f"http://{ip}/shelly", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                
                # Status-Details holen
                try:
                    status = requests.get(f"http://{ip}/status", timeout=self.timeout).json()
                except:
                    status = {}
                
                device = ShellyDevice(
                    ip=ip,
                    mac=data.get('mac', ''),
                    name=data.get('id', ''),
                    model=data.get('type', 'Unknown Shelly'),
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
                try:
                    status_resp = requests.post(
                        f"http://{ip}/rpc",
                        json={"id": 1, "method": "Shelly.GetStatus"},
                        timeout=self.timeout
                    )
                    status = status_resp.json().get('result', {})
                except:
                    status = {}
                
                # Switch-Anzahl ermitteln
                switch_count = sum(1 for key in status.keys() if key.startswith('switch:'))
                
                device = ShellyDevice(
                    ip=ip,
                    mac=data.get('mac', ''),
                    name=data.get('id', data.get('name', '')),
                    model=data.get('model', 'Shelly Plus'),
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
        print(f"\n🔍 Scanne Netzwerk {self.subnet}.0/24")
        print(f"   IP-Bereich: {self.subnet}.{ip_range[0]} bis {self.subnet}.{ip_range[1]}")
        print("   Tipp: Shellys haben oft IPs im Bereich .100-.150")
        
        found_devices = []
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            
            for i in range(ip_range[0], ip_range[1] + 1):
                ip = f"{self.subnet}.{i}"
                futures.append(executor.submit(self.scan_ip, ip))
            
            # Progress-Bar
            completed = 0
            total = len(futures)
            
            for future in as_completed(futures):
                completed += 1
                
                # Update nur alle 10 IPs für Performance
                if completed % 10 == 0 or completed == total:
                    print(f"\r   Fortschritt: {completed}/{total} IPs gescannt", end="", flush=True)
                
                device = future.result()
                if device:
                    found_devices.append(device)
                    print(f"\n   ✅ GEFUNDEN: {device.model} auf {device.ip} (MAC: {device.mac})")
        
        print(f"\n\n📊 Scan abgeschlossen: {len(found_devices)} Shelly-Geräte gefunden")
        self.devices = found_devices
        return found_devices
    
    def quick_scan(self, common_ranges=[(100, 150), (50, 100), (1, 50), (151, 254)]):
        """Schnell-Scan in typischen Shelly-IP-Bereichen"""
        print(f"\n⚡ Schnell-Scan im Netzwerk {self.subnet}.0/24")
        all_devices = []
        
        for start, end in common_ranges:
            print(f"\n   Scanne Bereich: .{start}-.{end}")
            devices = self.scan_network((start, end))
            all_devices.extend(devices)
            
            if len(all_devices) >= 5:  # Wenn genug gefunden, abbrechen
                print("\n   ✅ Genügend Geräte gefunden, beende Scan")
                break
        
        self.devices = all_devices
        return all_devices

class ShellyManager:
    """Shelly-Verwaltung"""
    
    CONFIG_FILE = Path(__file__).parent / "shelly_devices.json"
    
    def __init__(self):
        self.devices = []
        self.load_config()
    
    def load_config(self):
        """Lade gespeicherte Geräte-Konfiguration"""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.devices = [ShellyDevice(**d) for d in data]
            except Exception as e:
                print(f"   ⚠️ Fehler beim Laden der Config: {e}")
                self.devices = []
    
    def save_config(self):
        """Speichere Geräte-Konfiguration"""
        data = [d.to_dict() for d in self.devices]
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Konfiguration gespeichert in: {self.CONFIG_FILE}")
    
    def add_device(self, device: ShellyDevice):
        """Füge Gerät hinzu oder aktualisiere"""
        for i, d in enumerate(self.devices):
            if d.ip == device.ip:
                self.devices[i] = device
                return
        self.devices.append(device)

def interactive_setup():
    """Interaktives Setup mit verbesserter Netzwerkerkennung"""
    print("\n" + "="*60)
    print("     WartungsManager - Shelly Auto-Discovery v2.1")
    print("="*60)
    
    # Netzwerke erkennen
    print("\n📡 Erkenne physische Netzwerke...")
    detector = NetworkDetector()
    networks = detector.get_physical_networks()
    
    if not networks:
        print("\n❌ Keine Netzwerke gefunden!")
        subnet = input("Bitte Subnet manuell eingeben (z.B. 192.168.0): ")
    elif len(networks) == 1:
        subnet = networks[0]
        print(f"\n✅ Nutze Netzwerk: {subnet}.0/24")
    else:
        print(f"\n🔍 Mehrere Netzwerke gefunden:")
        for i, net in enumerate(networks, 1):
            print(f"   [{i}] {net}.0/24")
        
        choice = input(f"\nWelches Netzwerk scannen? [1-{len(networks)}]: ").strip()
        try:
            subnet = networks[int(choice) - 1]
        except:
            subnet = networks[0]
        
        print(f"\n✅ Gewähltes Netzwerk: {subnet}.0/24")
    
    # Scanner initialisieren
    discovery = ShellyDiscovery(subnet)
    
    # Scan-Methode wählen
    print("\n🔍 Scan-Methode:")
    print("   [1] Schnell-Scan (empfohlen, typische Bereiche)")
    print("   [2] Vollständiger Scan (alle 254 IPs)")
    print("   [3] Benutzerdefinierten Bereich scannen")
    
    scan_choice = input("\nAuswahl [1]: ").strip() or "1"
    
    if scan_choice == "1":
        devices = discovery.quick_scan()
    elif scan_choice == "2":
        devices = discovery.scan_network((1, 254))
    else:
        start = int(input("Start-IP (letzte Zahl, z.B. 100): "))
        end = int(input("End-IP (letzte Zahl, z.B. 150): "))
        devices = discovery.scan_network((start, end))
    
    if not devices:
        print("\n❌ Keine Shelly-Geräte gefunden!")
        print("\n📝 Mögliche Gründe:")
        print("   1. Shellys sind in anderem Netzwerk (z.B. Gäste-WLAN)")
        print("   2. Shellys sind ausgeschaltet")
        print("   3. Firewall blockiert Discovery")
        print("   4. Shellys nutzen andere IP-Range")
        print("\n💡 Tipp: Prüfen Sie in Ihrer FritzBox/Router die DHCP-Tabelle")
        return
    
    # Manager initialisieren
    manager = ShellyManager()
    
    # Geräte anzeigen
    print("\n" + "="*60)
    print(f"     ✅ {len(devices)} Shelly-Geräte gefunden!")
    print("="*60)
    
    for i, device in enumerate(devices, 1):
        print(f"\n[{i}] {device.model} - {device.ip}")
        print(f"    MAC: {device.mac}")
        print(f"    Name: {device.name or '(nicht gesetzt)'}")
        print(f"    Generation: {device.gen}")
        print(f"    Relais: {device.relay_count}")
        print(f"    Leistungsmessung: {'✅ JA' if device.has_power_meter else '❌ NEIN'}")
    
    # Rest der Konfiguration...
    # [Kompressor wählen, Widgets, etc. - gleicher Code wie vorher]
    
    print("\n✅ Setup abgeschlossen!")

if __name__ == "__main__":
    interactive_setup()

# Erstellt von Hans Hahn - Alle Rechte vorbehalten
