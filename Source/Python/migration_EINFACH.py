"""
EINFACHE Migration - Nur die notwendigen SQL-Befehle
"""

import sqlite3
import os
from datetime import datetime

def einfache_migration():
    """Führt nur die notwendigen SQL-Befehle aus"""
    
    # Datenbankpfad
    db_path = "database/wartungsmanager.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        print("💡 Versuchen Sie es aus dem richtigen Verzeichnis")
        return False
    
    print("🔧 Starte einfache Migration...")
    
    try:
        # Backup
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 Backup: {backup_path}")
        
        # Verbindung
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SQL-Befehle
        sql_befehle = [
            "ALTER TABLE flaschen ADD COLUMN interne_flaschennummer_auto BOOLEAN DEFAULT FALSE",
            "ALTER TABLE flaschen ADD COLUMN barcode_typ VARCHAR(20) DEFAULT 'CODE128'",
            "ALTER TABLE flaschen ADD COLUMN letzte_pruefung_protokoll TEXT",
            "ALTER TABLE flaschen ADD COLUMN pruefung_benachrichtigt BOOLEAN DEFAULT FALSE",
            "ALTER TABLE flaschen ADD COLUMN pruefung_benachrichtigung_datum DATE",
            "ALTER TABLE flaschen ADD COLUMN flaschen_gewicht_kg REAL",
            "ALTER TABLE flaschen ADD COLUMN ventil_typ VARCHAR(50)",
            "ALTER TABLE flaschen ADD COLUMN ursprungsland VARCHAR(50)",
            "ALTER TABLE flaschen ADD COLUMN kaufdatum DATE",
            "ALTER TABLE flaschen ADD COLUMN garantie_bis DATE",
            "ALTER TABLE flaschen ADD COLUMN externe_referenzen TEXT"
        ]
        
        # Befehle ausführen
        for sql in sql_befehle:
            try:
                cursor.execute(sql)
                spalte = sql.split("ADD COLUMN ")[1].split(" ")[0]
                print(f"✅ {spalte}")
            except sqlite3.Error as e:
                if "duplicate column" in str(e):
                    spalte = sql.split("ADD COLUMN ")[1].split(" ")[0]
                    print(f"⚠️ {spalte} bereits vorhanden")
                else:
                    print(f"❌ Fehler: {e}")
        
        # Speichern
        conn.commit()
        conn.close()
        
        print("✅ Migration abgeschlossen!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    einfache_migration()
