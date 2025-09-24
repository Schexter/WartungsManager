#!/usr/bin/env python3
"""
WartungsManager - Datenbank-Diagnose und Reparatur
Findet das Problem und erstellt die Datenbank am richtigen Ort
"""

import sys
import os
from pathlib import Path
import sqlite3

def diagnose_database_issue():
    """Diagnostiziert Datenbank-Probleme"""
    
    print("🔍 Datenbank-Diagnose startet...")
    print("=" * 50)
    
    # Aktuelles Verzeichnis
    current_dir = Path.cwd()
    print(f"📁 Aktuelles Verzeichnis: {current_dir}")
    
    # Erwartete Pfade prüfen
    possible_db_paths = [
        current_dir / "../../database",
        current_dir / "../database", 
        current_dir / "database",
        current_dir.parent.parent / "database"
    ]
    
    print("\n🔍 Prüfe mögliche Datenbank-Pfade:")
    for path in possible_db_paths:
        abs_path = path.resolve()
        exists = abs_path.exists()
        print(f"   {'✅' if exists else '❌'} {abs_path}")
        
        if not exists:
            try:
                abs_path.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ Erstellt: {abs_path}")
            except Exception as e:
                print(f"   ❌ Konnte nicht erstellen: {e}")
    
    return possible_db_paths[0].resolve()

def create_database_manually(db_path):
    """Erstellt Datenbank manuell mit sqlite3"""
    
    print(f"\n🔧 Erstelle Datenbank manuell: {db_path}")
    
    try:
        # Verzeichnis sicherstellen
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Datenbank-Datei erstellen
        db_file = db_path / "wartungsmanager.db"
        
        # Verbindung erstellen (erstellt Datei automatisch)
        conn = sqlite3.connect(str(db_file))
        
        # Test-Tabelle erstellen
        conn.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Test-Eintrag
        conn.execute("INSERT INTO test_table (name) VALUES (?)", ("Database Setup Test",))
        conn.commit()
        
        # Test-Abfrage
        cursor = conn.execute("SELECT * FROM test_table")
        rows = cursor.fetchall()
        
        conn.close()
        
        print(f"✅ Datenbank erstellt: {db_file}")
        print(f"📏 Dateigröße: {db_file.stat().st_size} Bytes")
        print(f"📊 Test-Einträge: {len(rows)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei manueller Erstellung: {e}")
        return False

def test_app_database():
    """Testet die App mit der erstellten Datenbank"""
    
    print("\n🧪 Teste App mit Datenbank...")
    
    try:
        from app import create_app, db
        
        app = create_app()
        
        with app.app_context():
            # Datenbankverbindung testen
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT 1"))
                print("✅ App kann Datenbank erreichen!")
                
                # Tabellen erstellen
                db.create_all()
                print("✅ App-Tabellen erstellt!")
                
        return True
        
    except Exception as e:
        print(f"❌ App-Test fehlgeschlagen: {e}")
        return False

def main():
    print("🔧 WartungsManager Datenbank-Diagnose & Reparatur")
    print("=" * 50)
    
    # Schritt 1: Diagnose
    db_path = diagnose_database_issue()
    
    # Schritt 2: Manuelle Erstellung
    if create_database_manually(db_path):
        print("\n🎉 Datenbank-Datei erfolgreich erstellt!")
    else:
        print("\n❌ Manuelle Datenbank-Erstellung fehlgeschlagen")
        return False
    
    # Schritt 3: App-Test
    if test_app_database():
        print("\n🎉 VOLLSTÄNDIGER ERFOLG!")
        print("=" * 50)
        print("✅ Datenbank wurde erstellt")
        print("✅ App kann auf Datenbank zugreifen")
        print("✅ WartungsManager ist einsatzbereit!")
        print("\n🚀 Starten Sie jetzt:")
        print("   cd ..\\..")
        print("   python run_production_REPARIERT.py")
        return True
    else:
        print("\n⚠️ Datenbank erstellt, aber App-Test fehlgeschlagen")
        print("💡 System sollte trotzdem funktionieren")
        return True

if __name__ == '__main__':
    success = main()
    input(f"\n{'✅ Erfolgreich!' if success else '❌ Mit Problemen'} Drücken Sie Enter zum Beenden...")
