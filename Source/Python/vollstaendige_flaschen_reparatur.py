"""
VOLLSTÄNDIGE Reparatur aller fehlenden Flaschen-Spalten
"""

import sqlite3
import os
from datetime import datetime

def vollstaendige_flaschen_reparatur():
    """Fügt ALLE fehlenden Flaschen-Spalten hinzu"""
    
    db_path = "database/wartungsmanager.db"
    
    print("🔧 VOLLSTÄNDIGE Flaschen-Reparatur...")
    
    try:
        # Verbindung
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Aktuelle Spalten prüfen
        cursor.execute("PRAGMA table_info(flaschen)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Vorhandene Spalten: {existing_columns}")
        
        # ALLE benötigten Spalten (Original + Neue)
        alle_spalten = [
            # Original-Felder die möglicherweise fehlen
            ('externe_flasche_nummer', 'VARCHAR(100)'),
            ('barcode', 'VARCHAR(100)'),
            ('bauart_zulassung', 'VARCHAR(100)'),
            ('seriennummer', 'VARCHAR(100)'),
            ('herstellungs_datum', 'DATE'),
            ('groesse_liter', 'REAL DEFAULT 11.0'),
            ('flaschen_typ', 'VARCHAR(50) DEFAULT "Standard"'),
            ('farbe', 'VARCHAR(30)'),
            ('hersteller', 'VARCHAR(100)'),
            ('pruef_datum', 'DATE'),
            ('naechste_pruefung', 'DATE'),
            ('max_druck_bar', 'INTEGER DEFAULT 300'),
            ('ist_aktiv', 'BOOLEAN DEFAULT TRUE'),
            ('ist_zum_fuellen_vorgemerkt', 'BOOLEAN DEFAULT FALSE'),
            ('letzter_fuellstand', 'REAL'),
            ('notizen', 'TEXT'),
            ('erstellt_am', 'DATETIME'),
            ('updated_at', 'DATETIME'),
            
            # Neue erweiterte Felder
            ('interne_flaschennummer_auto', 'BOOLEAN DEFAULT FALSE'),
            ('barcode_typ', 'VARCHAR(20) DEFAULT "CODE128"'),
            ('letzte_pruefung_protokoll', 'TEXT'),
            ('pruefung_benachrichtigt', 'BOOLEAN DEFAULT FALSE'),
            ('pruefung_benachrichtigung_datum', 'DATE'),
            ('flaschen_gewicht_kg', 'REAL'),
            ('ventil_typ', 'VARCHAR(50)'),
            ('ursprungsland', 'VARCHAR(50)'),
            ('kaufdatum', 'DATE'),
            ('garantie_bis', 'DATE'),
            ('externe_referenzen', 'TEXT'),
        ]
        
        # Fehlende Spalten hinzufügen
        added_count = 0
        for spalte, definition in alle_spalten:
            if spalte not in existing_columns:
                print(f"  ➕ Füge hinzu: {spalte}")
                try:
                    cursor.execute(f"ALTER TABLE flaschen ADD COLUMN {spalte} {definition}")
                    added_count += 1
                except sqlite3.Error as e:
                    print(f"    ⚠️ Fehler bei {spalte}: {e}")
            else:
                print(f"  ✅ Bereits vorhanden: {spalte}")
        
        print(f"\n📊 {added_count} Spalten hinzugefügt")
        
        # Prüfe finale Struktur
        cursor.execute("PRAGMA table_info(flaschen)")
        final_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Finale Spaltenanzahl: {len(final_columns)}")
        
        # Speichern
        conn.commit()
        conn.close()
        
        print("✅ Vollständige Reparatur abgeschlossen!")
        print("\n🧪 Teste nun den Server neu...")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    vollstaendige_flaschen_reparatur()
