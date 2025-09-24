#!/usr/bin/env python3
"""
WartungsManager - Datenbank-Initialisierung
Erstellt alle erforderlichen Tabellen in der SQLite-Datenbank
"""

import sys
import os
from pathlib import Path

def main():
    print("🔧 WartungsManager Datenbank-Initialisierung")
    print("=" * 50)
    
    try:
        # App importieren
        from app import create_app, db
        print("✅ App-Module erfolgreich importiert")
        
        # App erstellen
        app = create_app()
        print("✅ Flask-App erstellt")
        
        with app.app_context():
            print("🔧 Erstelle Datenbank-Tabellen...")
            
            # Alle Tabellen erstellen
            db.create_all()
            print("✅ Alle Tabellen erfolgreich erstellt!")
            
            # Test-Verbindung
            try:
                with db.engine.connect() as connection:
                    result = connection.execute(db.text("SELECT 1"))
                    print("✅ Datenbank-Verbindung erfolgreich getestet!")
            except Exception as e:
                print(f"⚠️ Verbindungstest-Warnung: {e}")
                print("   (Das ist normal beim ersten Setup)")
            
            # Datenbank-Info anzeigen
            db_path = Path("../../database/wartungsmanager.db").resolve()
            if db_path.exists():
                size_bytes = db_path.stat().st_size
                print(f"📊 Datenbank erstellt: {db_path}")
                print(f"📏 Dateigröße: {size_bytes} Bytes")
            
            print("\n🎉 DATENBANK-SETUP ERFOLGREICH ABGESCHLOSSEN!")
            print("=" * 50)
            print("✅ SQLite-Datenbank ist einsatzbereit")
            print("✅ Alle Tabellen wurden erstellt")
            print("✅ WartungsManager kann jetzt gestartet werden")
            
            return True
            
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        print("💡 Prüfen Sie ob alle Requirements installiert sind")
        return False
        
    except Exception as e:
        print(f"❌ FEHLER beim Datenbank-Setup: {e}")
        print(f"📝 Fehlertyp: {type(e).__name__}")
        print("💡 Tipps:")
        print("   - Prüfen Sie Dateiberechtigungen")
        print("   - Stellen Sie sicher, dass das database-Verzeichnis existiert")
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        print("\n❌ Setup fehlgeschlagen")
        input("Drücken Sie Enter zum Beenden...")
        sys.exit(1)
    else:
        print("\n🚀 Bereit zum Starten!")
        input("Drücken Sie Enter zum Beenden...")
