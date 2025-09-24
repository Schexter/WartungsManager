"""
NACHTRÄGLICHE Migration für fehlende externe_flasche_nummer Spalte
"""

import sqlite3
import os
from datetime import datetime

def repariere_externe_flasche_nummer():
    """Fügt die fehlende externe_flasche_nummer Spalte hinzu"""
    
    db_path = "database/wartungsmanager.db"
    
    print("🔧 Repariere fehlende externe_flasche_nummer Spalte...")
    
    try:
        # Verbindung
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfe ob Spalte existiert
        cursor.execute("PRAGMA table_info(flaschen)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'externe_flasche_nummer' not in columns:
            print("➕ Füge externe_flasche_nummer hinzu...")
            cursor.execute("ALTER TABLE flaschen ADD COLUMN externe_flasche_nummer VARCHAR(100)")
            print("✅ externe_flasche_nummer hinzugefügt")
        else:
            print("✅ externe_flasche_nummer bereits vorhanden")
        
        # Speichern
        conn.commit()
        conn.close()
        
        print("✅ Reparatur abgeschlossen!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    repariere_externe_flasche_nummer()
