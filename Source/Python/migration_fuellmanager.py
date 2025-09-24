"""
Migration für Füllmanager Erweiterung
Fügt neue Tabellen für erweiterten Füllmanager mit Unterschriftenfunktion hinzu
"""

from app import create_app, db
from app.models.fuellmanager import FuellManager, FuellManagerSignatur, FuellVorgangErweitert
from app.models.fuellmanager.preiskonfiguration import GasPreisKonfiguration
from sqlalchemy import text
import sys

def migrate_fuellmanager():
    """Führt die Migration für den Füllmanager durch"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Starte Füllmanager Migration...")
            
            # Prüfe ob Tabellen bereits existieren
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            # Erstelle neue Tabellen wenn nicht vorhanden
            tables_to_create = []
            
            if 'fuellmanager' not in existing_tables:
                tables_to_create.append('fuellmanager')
                print("📋 Tabelle 'fuellmanager' wird erstellt...")
            
            if 'fuellmanager_signaturen' not in existing_tables:
                tables_to_create.append('fuellmanager_signaturen')
                print("📋 Tabelle 'fuellmanager_signaturen' wird erstellt...")
            
            if 'fuellvorgang_erweitert' not in existing_tables:
                tables_to_create.append('fuellvorgang_erweitert')
                print("📋 Tabelle 'fuellvorgang_erweitert' wird erstellt...")
            
            if 'gas_preis_konfiguration' not in existing_tables:
                tables_to_create.append('gas_preis_konfiguration')
                print("📋 Tabelle 'gas_preis_konfiguration' wird erstellt...")
            
            if not tables_to_create:
                print("✅ Alle Füllmanager-Tabellen existieren bereits!")
                return True
            
            # Erstelle die Tabellen
            db.create_all()
            
            print("✅ Füllmanager-Tabellen erfolgreich erstellt!")
            
            # Zeige erstellte Tabellen
            print("\n📊 Erstellte Tabellen:")
            for table in tables_to_create:
                print(f"   - {table}")
            
            # Validiere die Erstellung
            inspector = db.inspect(db.engine)
            new_tables = inspector.get_table_names()
            
            all_created = all(table in new_tables for table in ['fuellmanager', 'fuellmanager_signaturen', 'fuellvorgang_erweitert', 'gas_preis_konfiguration'])
            
            if all_created:
                print("\n✅ Migration erfolgreich abgeschlossen!")
                return True
            else:
                print("\n❌ Fehler: Nicht alle Tabellen wurden erstellt!")
                return False
                
        except Exception as e:
            print(f"\n❌ Fehler bei der Migration: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def show_table_info():
    """Zeigt Informationen über die Füllmanager-Tabellen"""
    app = create_app()
    
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            
            print("\n📊 Füllmanager Tabellen-Information:")
            
            tables = ['fuellmanager', 'fuellmanager_signaturen', 'fuellvorgang_erweitert', 'gas_preis_konfiguration']
            
            for table_name in tables:
                if table_name in inspector.get_table_names():
                    print(f"\n📋 Tabelle: {table_name}")
                    columns = inspector.get_columns(table_name)
                    print("   Spalten:")
                    for col in columns:
                        print(f"      - {col['name']} ({col['type']})")
                else:
                    print(f"\n❌ Tabelle '{table_name}' existiert nicht!")
                    
        except Exception as e:
            print(f"\n❌ Fehler beim Abrufen der Tabellen-Info: {str(e)}")


if __name__ == '__main__':
    print("=" * 60)
    print("Füllmanager Migration")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'info':
        show_table_info()
    else:
        success = migrate_fuellmanager()
        if success:
            show_table_info()
        else:
            print("\n⚠️  Migration fehlgeschlagen!")
            sys.exit(1)
