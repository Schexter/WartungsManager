# Datenbank-Check und Repair für Füllmanager
# Erstellt von Hans Hahn - Alle Rechte vorbehalten
# Datum: 04.07.2025

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.fuellmanager import FuellManager, FuellManagerSignatur, FuellVorgangErweitert
from app.models.fuellmanager.preiskonfiguration import GasPreisKonfiguration
from sqlalchemy import inspect

def check_fuellmanager_tables():
    """Prüft ob Füllmanager-Tabellen existieren"""
    app = create_app()
    
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print("=== FÜLLMANAGER TABELLEN CHECK ===")
        print(f"Vorhandene Tabellen: {len(existing_tables)}")
        
        required_tables = [
            'fuellmanager',
            'fuellmanager_signaturen', 
            'fuellvorgang_erweitert',
            'gas_preis_konfiguration'
        ]
        
        missing_tables = []
        for table in required_tables:
            if table in existing_tables:
                print(f"✓ {table} - VORHANDEN")
            else:
                print(f"✗ {table} - FEHLT!")
                missing_tables.append(table)
        
        if missing_tables:
            print("\n=== ERSTELLE FEHLENDE TABELLEN ===")
            try:
                # Erstelle nur die fehlenden Tabellen
                db.create_all()
                print("✓ Tabellen erfolgreich erstellt!")
                
                # Initialisiere Standard-Preise
                print("\n=== INITIALISIERE STANDARD-PREISE ===")
                GasPreisKonfiguration.initialisiere_standard_preise()
                print("✓ Standard-Preise initialisiert!")
                
            except Exception as e:
                print(f"✗ Fehler beim Erstellen der Tabellen: {str(e)}")
                return False
        else:
            print("\n✓ Alle Füllmanager-Tabellen sind vorhanden!")
        
        # Zeige aktuelle Statistiken
        try:
            fuellungen_count = FuellManager.query.count()
            preise_count = GasPreisKonfiguration.query.count()
            
            print(f"\n=== STATISTIKEN ===")
            print(f"Füllvorgänge: {fuellungen_count}")
            print(f"Preiskonfigurationen: {preise_count}")
            
        except Exception as e:
            print(f"\nFehler beim Laden der Statistiken: {str(e)}")
        
        return len(missing_tables) == 0

if __name__ == '__main__':
    success = check_fuellmanager_tables()
    sys.exit(0 if success else 1)
