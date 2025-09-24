"""
Initialisiert die Datenbank im Production-Pfad C:\database\
"""
import os
import sys

# Set environment variable for production database path
os.environ['DATABASE_URL'] = 'sqlite:///C:/database/wartungsmanager.db'

from app import create_app, db

print("Datenbank-Initialisierung startet...")
print(f"Ziel-Pfad: C:\\database\\wartungsmanager.db")

# App mit production config erstellen
app = create_app('production')

with app.app_context():
    try:
        # Alle Tabellen erstellen
        db.create_all()
        print("Alle Tabellen erfolgreich erstellt!")

        # Test-Verbindung
        result = db.session.execute(db.text("SELECT 1"))
        print("Datenbank-Verbindung erfolgreich getestet!")

        # Prüfe ob Datei erstellt wurde
        if os.path.exists('C:/database/wartungsmanager.db'):
            size = os.path.getsize('C:/database/wartungsmanager.db')
            print(f"Datenbank erfolgreich erstellt: {size} bytes")

        print("Datenbank-Setup abgeschlossen!")

    except Exception as e:
        print(f"FEHLER beim Datenbank-Setup: {e}")
        print("Tipp: Pruefen Sie Dateiberechtigungen im database-Ordner")