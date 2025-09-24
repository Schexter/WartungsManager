#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Script für Kompressor Reset-Funktionalität
PASSWORT: Magicfactory15!

Dieses Script testet die neue Reset-API
"""

import requests
import json
from datetime import datetime

# API-Basis URL (anpassen falls nötig)
BASE_URL = "http://localhost:5000/api/kompressor"

def test_kompressor_reset():
    """Testet die Reset-Funktionalität"""
    
    print("🔧 KOMPRESSOR RESET-TEST")
    print("=" * 50)
    
    # 1. Aktuellen Status abrufen
    print("1. Aktueller Kompressor-Status:")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   Kompressor AN: {status.get('ist_an', False)}")
            if status.get('aktiver_kompressor'):
                aktiver = status['aktiver_kompressor']
                print(f"   Füller: {aktiver.get('fueller', 'N/A')}")
                print(f"   Start-Zeit: {aktiver.get('start_zeit', 'N/A')}")
                print(f"   Aktuell aktiv: {aktiver.get('ist_aktiv', False)}")
        else:
            print(f"   ❌ Status-Abfrage fehlgeschlagen: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Fehler bei Status-Abfrage: {e}")
    
    print()
    
    # 2. Reset mit korrektem Passwort testen
    print("2. Reset mit korrektem Passwort:")
    reset_data = {
        "passwort": "Magicfactory15!",
        "grund": "Test des Reset-Systems"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/reset", 
            json=reset_data,
            headers={'Content-Type': 'application/json'}
        )
        
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print("   ✅ Reset erfolgreich!")
            if 'reset_info' in result:
                info = result['reset_info']
                print(f"   Alte Laufzeit: {info.get('alte_laufzeit_minuten', 0):.1f} Minuten")
                print(f"   Neue Start-Zeit: {info.get('neue_startzeit', 'N/A')}")
                print(f"   Grund: {info.get('grund', 'N/A')}")
        else:
            print(f"   ❌ Reset fehlgeschlagen: {result.get('error', 'Unbekannter Fehler')}")
            
    except Exception as e:
        print(f"   ❌ Fehler beim Reset: {e}")
    
    print()
    
    # 3. Reset mit falschem Passwort testen (Sicherheitstest)
    print("3. Sicherheitstest - Reset mit falschem Passwort:")
    wrong_data = {
        "passwort": "falsch123",
        "grund": "Sicherheitstest"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/reset", 
            json=wrong_data,
            headers={'Content-Type': 'application/json'}
        )
        
        result = response.json()
        
        if response.status_code == 400 and not result.get('success'):
            print("   ✅ Sicherheit OK - Falsches Passwort abgelehnt")
            print(f"   Fehlermeldung: {result.get('error', 'N/A')}")
        else:
            print("   ❌ SICHERHEITSPROBLEM: Falsches Passwort wurde akzeptiert!")
            
    except Exception as e:
        print(f"   ❌ Fehler beim Sicherheitstest: {e}")
    
    print()
    
    # 4. Status nach Reset prüfen
    print("4. Status nach Reset:")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   Kompressor AN: {status.get('ist_an', False)}")
            if status.get('aktiver_kompressor'):
                aktiver = status['aktiver_kompressor']
                print(f"   Neue Start-Zeit: {aktiver.get('start_zeit', 'N/A')}")
                print(f"   Status: {aktiver.get('status', 'N/A')}")
        else:
            print(f"   ❌ Status-Abfrage fehlgeschlagen: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Fehler bei Status-Abfrage: {e}")
    
    print()
    print("🎯 Test abgeschlossen!")
    print("=" * 50)

if __name__ == "__main__":
    print(f"Test gestartet um: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    test_kompressor_reset()
