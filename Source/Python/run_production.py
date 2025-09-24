#!/usr/bin/env python3
"""    
WartungsManager - Production Runner mit C:\\database\\ Pfad
"""

import os
import sys
import socket
from pathlib import Path

# .env Datei laden falls vorhanden
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Umgebungsvariablen geladen aus: {env_path}")
except ImportError:
    print("⚠️  python-dotenv nicht installiert - .env wird ignoriert")
    print("   Installation: pip install python-dotenv")

# Production database path setzen (kann durch .env überschrieben werden)
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = 'sqlite:///C:/database/wartungsmanager.db'
if 'FLASK_ENV' not in os.environ:
    os.environ['FLASK_ENV'] = 'production'

# Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

# App mit production config erstellen
app = create_app('production')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("     WartungsManager - Production Mode")
    print("="*60)
    print(f"Datenbank: C:\\database\\wartungsmanager.db")
    print(f"Touch-optimierte UI verfuegbar auf: http://localhost:5000")
    
    # Shelly-Status anzeigen
    shelly_enabled = os.getenv('SHELLY_ENABLED', 'false').lower() == 'true'
    if shelly_enabled:
        print(f"\n✅ Shelly-Integration AKTIVIERT")
        print(f"   IP: {os.getenv('SHELLY_IP', 'nicht gesetzt')}")
        print(f"   Modell: {os.getenv('SHELLY_MODEL', 'nicht gesetzt')}")
    else:
        print(f"\n⚠️  Shelly-Integration DEAKTIVIERT")
        print(f"   Zum Aktivieren: python configure_shelly.py")

    # Echte IP-Adresse anzeigen
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Entwicklungsrechner IP: {local_ip}")
    print(f"Direkter Zugriff: http://{local_ip}:5000")
    print(f"Python Version: {sys.version}")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,  # Für Development, in echter Production auf False setzen
        threaded=True
    )