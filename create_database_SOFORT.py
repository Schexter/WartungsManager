#!/usr/bin/env python3
"""
Sofortige Datenbank-Erstellung für WartungsManager
Erstellt eine funktionierende SQLite-Datenbank mit allen Tabellen
"""

import sqlite3
import os
from pathlib import Path

def create_database_directly():
    """Erstellt Datenbank direkt mit sqlite3"""
    
    # Pfad zur Datenbank
    db_dir = Path("C:/SoftwareEntwicklung/WartungsManager-main/database")
    db_dir.mkdir(exist_ok=True)
    
    db_path = db_dir / "wartungsmanager.db"
    
    print(f"Erstelle Datenbank: {db_path}")
    
    # Verbindung erstellen (erstellt Datei automatisch)
    conn = sqlite3.connect(str(db_path))
    
    # Basis-Tabellen erstellen
    cursor = conn.cursor()
    
    # Users Tabelle
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120),
            password_hash VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Kunden Tabelle
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kunden (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(120),
            telefon VARCHAR(50),
            adresse TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Flaschen Tabelle
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flaschen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nummer VARCHAR(50) UNIQUE NOT NULL,
            kunde_id INTEGER,
            typ VARCHAR(50),
            inhalt VARCHAR(50),
            status VARCHAR(50) DEFAULT 'eingegangen',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kunde_id) REFERENCES kunden (id)
        )
    """)
    
    # Kompressor Tabelle
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kompressor_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status VARCHAR(50) NOT NULL,
            temperatur FLOAT,
            druck FLOAT,
            laufzeit_minuten INTEGER DEFAULT 0,
            letzter_service DATE,
            naechster_service DATE,
            notizen TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Füllaufträge Tabelle
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fuellauftraege (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kunde_id INTEGER,
            flasche_id INTEGER,
            gas_typ VARCHAR(50),
            druck_bar INTEGER,
            status VARCHAR(50) DEFAULT 'offen',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME,
            FOREIGN KEY (kunde_id) REFERENCES kunden (id),
            FOREIGN KEY (flasche_id) REFERENCES flaschen (id)
        )
    """)
    
    # Test-Daten einfügen
    cursor.execute("""
        INSERT OR IGNORE INTO kompressor_status 
        (status, temperatur, druck, laufzeit_minuten, notizen)
        VALUES ('ausgeschaltet', 25.0, 0.0, 0, 'System initialisiert')
    """)
    
    cursor.execute("""
        INSERT OR IGNORE INTO kunden (name, email, telefon)
        VALUES ('Test Kunde', 'test@example.com', '0123456789')
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Datenbank erfolgreich erstellt!")
    print(f"📁 Speicherort: {db_path}")
    print(f"📊 Dateigröße: {db_path.stat().st_size} Bytes")
    
    return True

if __name__ == '__main__':
    try:
        create_database_directly()
        print("\n🎉 DATENBANK SETUP ERFOLGREICH!")
        print("Das System sollte jetzt ohne Fehler laufen.")
        print("\nStarten Sie den WartungsManager neu:")
        print("python run_production_REPARIERT.py")
    except Exception as e:
        print(f"❌ Fehler: {e}")
