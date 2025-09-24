#!/usr/bin/env python3
"""
Datenbank-Pfad-Reparatur für WartungsManager
Kopiert die Datenbank an den richtigen Ort wo die App sie findet
"""

import shutil
from pathlib import Path
import os

def fix_database_path():
    """Repariert den Datenbank-Pfad"""
    
    print("🔧 Repariere Datenbank-Pfad...")
    
    # Quell-Datenbank (wo wir sie erstellt haben)
    source_db = Path("C:/SoftwareEntwicklung/WartungsManager-main/database/wartungsmanager.db")
    
    # Ziel-Pfad (wo die App sie sucht - relativ zu Source/Python)
    target_dir = Path("C:/SoftwareEntwicklung/WartungsManager-main/Source/Python/database")
    target_db = target_dir / "wartungsmanager.db"
    
    print(f"📂 Quell-DB: {source_db}")
    print(f"📂 Ziel-DB: {target_db}")
    
    # Ziel-Verzeichnis erstellen
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Verzeichnis erstellt: {target_dir}")
    
    # Datenbank kopieren
    if source_db.exists():
        shutil.copy2(source_db, target_db)
        print(f"✅ Datenbank kopiert!")
        print(f"📊 Größe: {target_db.stat().st_size} Bytes")
        return True
    else:
        print(f"❌ Quell-Datenbank nicht gefunden: {source_db}")
        return False

def verify_database():
    """Überprüft ob die Datenbank am richtigen Ort ist"""
    
    # Arbeitsverzeichnis der App simulieren
    app_db_path = Path("C:/SoftwareEntwicklung/WartungsManager-main/Source/Python/database/wartungsmanager.db")
    
    if app_db_path.exists():
        print(f"✅ Datenbank gefunden: {app_db_path}")
        print(f"📊 Größe: {app_db_path.stat().st_size} Bytes")
        
        # Test-Verbindung
        import sqlite3
        try:
            conn = sqlite3.connect(str(app_db_path))
            cursor = conn.execute("SELECT COUNT(*) FROM users")
            print(f"✅ Datenbank-Verbindung erfolgreich")
            conn.close()
            return True
        except Exception as e:
            print(f"⚠️ DB-Verbindungstest: {e}")
            return False
    else:
        print(f"❌ Datenbank nicht gefunden: {app_db_path}")
        return False

def main():
    print("🔧 WartungsManager Datenbank-Pfad-Reparatur")
    print("=" * 50)
    
    # Schritt 1: Datenbank an richtigen Ort kopieren
    if fix_database_path():
        print("\n✅ Datenbank erfolgreich kopiert!")
    else:
        print("\n❌ Kopieren fehlgeschlagen!")
        return False
    
    # Schritt 2: Überprüfung
    print("\n🔍 Überprüfe Datenbank...")
    if verify_database():
        print("\n🎉 REPARATUR ERFOLGREICH!")
        print("=" * 50)
        print("✅ Datenbank ist am richtigen Ort")
        print("✅ Verbindung funktioniert")
        print("✅ App sollte jetzt ohne Fehler laufen")
        print("\n🚀 Starten Sie den WartungsManager neu:")
        print("python run_production_REPARIERT.py")
        return True
    else:
        print("\n❌ Überprüfung fehlgeschlagen")
        return False

if __name__ == '__main__':
    main()
