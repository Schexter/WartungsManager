#!/usr/bin/env python3
"""
Datenbank-Migration Script für WartungsManager
Erstellt die neuen Kompressor-System Tabellen

Aufruf: python run_migration.py
"""

import os
import sys
import logging
from pathlib import Path

# Flask App Setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate, upgrade
    from config.config import Config
    
    # App erstellen
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # SQLAlchemy initialisieren
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    
    # Logging konfigurieren
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    def run_migration():
        """Führt die Datenbank-Migration aus"""
        
        print("🔄 WartungsManager - Datenbank Migration")
        print("=" * 50)
        print("Erstellt die neuen Kompressor-System Tabellen:")
        print("  ✓ kompressor_betrieb")
        print("  ✓ kunden")
        print("  ✓ flaschen") 
        print("  ✓ bulk_fuellvorgaenge")
        print("  ✓ flasche_fuellvorgang")
        print("=" * 50)
        
        try:
            with app.app_context():
                # Prüfe ob Migration nötig ist
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                existing_tables = inspector.get_table_names()
                
                if 'kompressor_betrieb' in existing_tables:
                    print("ℹ️  Kompressor-System Tabellen bereits vorhanden.")
                    print("   Migration bereits durchgeführt.")
                    return True
                
                print("🚀 Starte Migration...")
                
                # Führe Migration aus
                upgrade()
                
                # Verifiziere Ergebnis
                inspector = inspect(db.engine)
                new_tables = inspector.get_table_names()
                
                required_tables = [
                    'kompressor_betrieb',
                    'kunden', 
                    'flaschen',
                    'bulk_fuellvorgaenge',
                    'flasche_fuellvorgang'
                ]
                
                success = True
                for table in required_tables:
                    if table in new_tables:
                        print(f"  ✅ Tabelle '{table}' erstellt")
                    else:
                        print(f"  ❌ Tabelle '{table}' FEHLT")
                        success = False
                
                if success:
                    print()
                    print("🎉 Migration erfolgreich abgeschlossen!")
                    print("   Das WartungsManager System ist jetzt bereit.")
                    print()
                    print("   Sie können jetzt die Anwendung starten:")
                    print("   python run.py")
                    print()
                else:
                    print("❌ Migration teilweise fehlgeschlagen!")
                    return False
                    
                return True
                
        except Exception as e:
            logger.error(f"Migration fehlgeschlagen: {str(e)}")
            print(f"❌ FEHLER: {str(e)}")
            print()
            print("Mögliche Lösungen:")
            print("1. Überprüfen Sie die Datenbank-Konfiguration")
            print("2. Stellen Sie sicher, dass die DB-Datei beschreibbar ist")
            print("3. Führen Sie das Script als Administrator aus")
            return False
    
    def check_database_status():
        """Prüft den aktuellen Status der Datenbank"""
        
        try:
            with app.app_context():
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                
                print("📊 Datenbank-Status:")
                print("=" * 30)
                
                required_tables = [
                    'users',
                    'handbefuellungen', 
                    'wartungen',
                    'fuellvorgaenge',
                    'kompressor_betrieb',
                    'kunden',
                    'flaschen',
                    'bulk_fuellvorgaenge',
                    'flasche_fuellvorgang'
                ]
                
                for table in required_tables:
                    status = "✅" if table in tables else "❌"
                    print(f"  {status} {table}")
                
                missing_tables = [t for t in required_tables if t not in tables]
                
                if missing_tables:
                    print()
                    print(f"⚠️  {len(missing_tables)} Tabelle(n) fehlen:")
                    for table in missing_tables:
                        print(f"     • {table}")
                    print()
                    print("   → Migration erforderlich!")
                else:
                    print()
                    print("✅ Alle Tabellen vorhanden - System bereit!")
                
                return len(missing_tables) == 0
                
        except Exception as e:
            print(f"❌ Fehler beim Datenbankstatus-Check: {str(e)}")
            return False
    
    if __name__ == "__main__":
        print()
        
        # Argumentbehandlung
        if len(sys.argv) > 1:
            if sys.argv[1] == "status":
                check_database_status()
                sys.exit(0)
            elif sys.argv[1] == "help":
                print("WartungsManager Migration Script")
                print("Verwendung:")
                print("  python run_migration.py       - Migration ausführen")
                print("  python run_migration.py status - Datenbank-Status prüfen")
                print("  python run_migration.py help   - Diese Hilfe anzeigen")
                sys.exit(0)
        
        # Standard: Migration ausführen
        if check_database_status():
            print("Keine Migration erforderlich.")
        else:
            success = run_migration()
            sys.exit(0 if success else 1)

except ImportError as e:
    print("❌ FEHLER: Fehlende Abhängigkeiten")
    print(f"   {str(e)}")
    print()
    print("Lösungen:")
    print("1. Virtual Environment aktivieren:")
    print("   wartung_env\\Scripts\\activate")
    print()
    print("2. Dependencies installieren:")
    print("   pip install -r requirements.txt")
    print()
    sys.exit(1)

except Exception as e:
    print(f"❌ UNERWARTETER FEHLER: {str(e)}")
    sys.exit(1)
