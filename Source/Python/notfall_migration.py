#!/usr/bin/env python3
"""
NOTFALL-MIGRATION ohne Virtual Environment
Verwendet System-Python direkt

Aufruf: python notfall_migration.py
"""

import os
import sys
import sqlite3
from datetime import datetime, date

def create_database_tables():
    """Erstellt die Kompressor-System Tabellen direkt in SQLite"""
    
    db_path = os.path.join('database', 'wartungsmanager.db')
    
    print("🔄 Notfall-Migration für WartungsManager")
    print("=" * 50)
    print(f"Datenbank-Pfad: {db_path}")
    
    if not os.path.exists('database'):
        os.makedirs('database')
        print("✓ Database-Verzeichnis erstellt")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfe ob Tabellen bereits existieren
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kompressor_betrieb'")
        if cursor.fetchone():
            print("ℹ️  Kompressor-Tabellen bereits vorhanden")
            print("   Migration bereits durchgeführt.")
            conn.close()
            return True
        
        print("🚀 Erstelle Kompressor-System Tabellen...")
        
        # Kunden Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kunden (
                id INTEGER PRIMARY KEY,
                mitgliedsnummer VARCHAR(20) UNIQUE,
                vorname VARCHAR(100) NOT NULL,
                nachname VARCHAR(100) NOT NULL,
                firma VARCHAR(200),
                email VARCHAR(150),
                telefon VARCHAR(30),
                strasse VARCHAR(200),
                plz VARCHAR(10),
                ort VARCHAR(100),
                land VARCHAR(50),
                geburtsdatum DATE,
                mitgliedschaft_typ VARCHAR(50),
                mitgliedschaft_start DATE,
                mitgliedschaft_ende DATE,
                notizen TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("  ✅ Tabelle 'kunden' erstellt")
        
        # Kompressor Betrieb Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kompressor_betrieb (
                id INTEGER PRIMARY KEY,
                start_zeit DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                end_zeit DATETIME,
                betriebsdauer_minuten INTEGER,
                oel_getestet BOOLEAN NOT NULL DEFAULT 0,
                oel_test_ergebnis VARCHAR(10),
                oel_tester VARCHAR(100),
                oel_tester_id INTEGER,
                fueller VARCHAR(100) NOT NULL,
                fueller_id INTEGER,
                status VARCHAR(20) NOT NULL DEFAULT 'laufend',
                notizen TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fueller_id) REFERENCES users (id),
                FOREIGN KEY (oel_tester_id) REFERENCES users (id)
            )
        ''')
        print("  ✅ Tabelle 'kompressor_betrieb' erstellt")
        
        # Flaschen Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flaschen (
                id INTEGER PRIMARY KEY,
                seriennummer VARCHAR(50) NOT NULL UNIQUE,
                flaschennummer VARCHAR(50),
                kunde_id INTEGER NOT NULL,
                groesse_liter FLOAT NOT NULL,
                flaschen_typ VARCHAR(50),
                farbe VARCHAR(30),
                hersteller VARCHAR(100),
                herstellungsjahr INTEGER,
                max_druck_bar INTEGER,
                letztes_pruef_datum DATE,
                naechste_pruefung DATE,
                tuv_pruefstelle VARCHAR(100),
                notizen TEXT,
                is_active BOOLEAN DEFAULT 1,
                vorgemerkt BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (kunde_id) REFERENCES kunden (id)
            )
        ''')
        print("  ✅ Tabelle 'flaschen' erstellt")
        
        # Bulk Füllvorgänge Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bulk_fuellvorgaenge (
                id INTEGER PRIMARY KEY,
                start_zeit DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                end_zeit DATETIME,
                operator VARCHAR(100) NOT NULL,
                operator_id INTEGER,
                status VARCHAR(20) NOT NULL DEFAULT 'erstellt',
                anzahl_flaschen INTEGER DEFAULT 0,
                flaschen_gefuellt INTEGER DEFAULT 0,
                flaschen_fehlgeschlagen INTEGER DEFAULT 0,
                notizen TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (operator_id) REFERENCES users (id)
            )
        ''')
        print("  ✅ Tabelle 'bulk_fuellvorgaenge' erstellt")
        
        # Flasche-Füllvorgang Relation Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flasche_fuellvorgang (
                id INTEGER PRIMARY KEY,
                bulk_vorgang_id INTEGER NOT NULL,
                flasche_id INTEGER NOT NULL,
                ziel_druck INTEGER NOT NULL,
                erreicher_druck INTEGER,
                status VARCHAR(20) NOT NULL DEFAULT 'bereit',
                start_zeit DATETIME,
                end_zeit DATETIME,
                grund VARCHAR(200),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bulk_vorgang_id) REFERENCES bulk_fuellvorgaenge (id),
                FOREIGN KEY (flasche_id) REFERENCES flaschen (id)
            )
        ''')
        print("  ✅ Tabelle 'flasche_fuellvorgang' erstellt")
        
        # Beispiel-Daten einfügen
        cursor.execute('''
            INSERT OR IGNORE INTO kunden 
            (mitgliedsnummer, vorname, nachname, email, telefon, mitgliedschaft_typ, is_active)
            VALUES 
            ('M-001', 'Max', 'Mustermann', 'max@beispiel.de', '0123-456789', 'Standard', 1)
        ''')
        
        cursor.execute('SELECT id FROM kunden WHERE mitgliedsnummer = "M-001"')
        kunde_id = cursor.fetchone()
        
        if kunde_id:
            cursor.execute('''
                INSERT OR IGNORE INTO flaschen 
                (seriennummer, flaschennummer, kunde_id, groesse_liter, flaschen_typ, max_druck_bar, is_active)
                VALUES 
                ('F-001', 'Flasche-001', ?, 11.0, 'Standard', 300, 1)
            ''', (kunde_id[0],))
            print("  ✅ Beispiel-Daten erstellt")
        
        conn.commit()
        conn.close()
        
        print()
        print("🎉 Notfall-Migration erfolgreich abgeschlossen!")
        print("   Alle Kompressor-System Tabellen wurden erstellt.")
        print()
        print("Sie können jetzt die Anwendung starten:")
        print("python run.py")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ FEHLER: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

def check_tables():
    """Prüft welche Tabellen vorhanden sind"""
    
    db_path = os.path.join('database', 'wartungsmanager.db')
    
    if not os.path.exists(db_path):
        print("❌ Datenbank-Datei nicht gefunden")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("📊 Datenbank-Tabellen:")
        print("=" * 30)
        
        required_tables = [
            'users', 'handbefuellungen', 'wartungen', 'fuellvorgaenge',
            'kompressor_betrieb', 'kunden', 'flaschen', 
            'bulk_fuellvorgaenge', 'flasche_fuellvorgang'
        ]
        
        for table in required_tables:
            status = "✅" if table in tables else "❌"
            print(f"  {status} {table}")
        
        missing = [t for t in required_tables if t not in tables]
        
        conn.close()
        
        if missing:
            print(f"\n⚠️  {len(missing)} Tabelle(n) fehlen - Migration erforderlich")
            return False
        else:
            print("\n✅ Alle Tabellen vorhanden!")
            return True
            
    except Exception as e:
        print(f"❌ Fehler beim Tabellen-Check: {str(e)}")
        return False

if __name__ == "__main__":
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_tables()
    else:
        if check_tables():
            print("Keine Migration erforderlich.")
        else:
            create_database_tables()
    
    print()
    input("Drücken Sie Enter zum Beenden...")
