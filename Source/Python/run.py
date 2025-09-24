#!/usr/bin/env python3
"""
WartungsManager - Touch-optimierte Wartungs- und Füllstandsmanagement-Anwendung

Entry Point für die Flask Web-Anwendung
Python 3.11 + Flask + SQLite + Touch-UI

Führe aus mit:
    python run.py

Für Production mit Gunicorn:
    gunicorn --bind 192.168.1.100:5000 --workers 4 wsgi:app
"""

import os
import sys
# Fügt das aktuelle Verzeichnis zum Python-Pfad hinzu, um 'app' zu finden
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.fuelling import Fuellvorgang
from app.models.maintenance import Wartung
from app.models.protocol import Handbefuellung
from app.models.users import User, create_default_users
from flask_migrate import upgrade

# Environment und Konfiguration laden
config_name = os.getenv('FLASK_ENV') or 'default'
app = create_app(config_name)

@app.shell_context_processor
def make_shell_context():
    """Shell Context für Flask CLI"""
    return {
        'db': db,
        'Fuellvorgang': Fuellvorgang,
        'Wartung': Wartung,
        'Handbefuellung': Handbefuellung,
        'User': User
    }

@app.cli.command()
def deploy():
    """Führt Deployment-Aufgaben aus."""
    # Datenbank migrieren
    with app.app_context():
        upgrade()
        # Standardbenutzer erstellen
        create_default_users()
    print("Deployment abgeschlossen.")

@app.cli.command("init-db")
def init_db_command():
    """Initialisiert die Datenbank und erstellt Standardbenutzer."""
    with app.app_context():
        upgrade()
        create_default_users()
    print("Datenbank initialisiert und Standardbenutzer erstellt.")

@app.cli.command()
def test():
    """Unit Tests ausführen"""
    import pytest
    pytest.main(['-v', 'tests/'])

if __name__ == '__main__':
    # Development Server
    print("WartungsManager startet...")
    print(f"Touch-optimierte UI verfuegbar auf: http://localhost:5000")
    print(f"Netzwerk-Zugriff: http://192.168.0.50:5000")
    print(f"Von allen Netzwerk-Geraeten: http://[PC-IP]:5000")
    print(f"Python Version: {sys.version}")
    
    # Echte IP-Adresse anzeigen
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Entwicklungsrechner IP: {local_ip}")
    print(f"Direkter Zugriff: http://{local_ip}:5000")
    
    app.run(
        host='0.0.0.0',  # WICHTIG: Alle Netzwerk-Interfaces
        port=5000,       # Standard Flask Port
        debug=True,      # Development Mode
        threaded=True    # Multi-Threading Support
    )
