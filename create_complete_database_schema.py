#!/usr/bin/env python3
"""
Vollständige Datenbank-Schema-Erstellung für WartungsManager
Erstellt alle Tabellen entsprechend den Modell-Definitionen der App
"""

import sqlite3
from pathlib import Path

def create_complete_database():
    """Erstellt vollständige Datenbank mit korrektem Schema"""
    
    db_path = Path("C:/SoftwareEntwicklung/WartungsManager-main/Source/Python/database/wartungsmanager.db")
    
    print(f"🔧 Erstelle vollständige Datenbank: {db_path}")
    
    # Alte Datenbank löschen
    if db_path.exists():
        db_path.unlink()
        print("🗑️ Alte Datenbank gelöscht")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # ============= ALLE TABELLEN NACH APP-SCHEMA =============
    
    # 1. KUNDEN (mit allen Spalten aus dem Fehler-Log)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kunden (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mitgliedsnummer VARCHAR(50) UNIQUE,
            externe_kundennummer VARCHAR(50),
            externe_system VARCHAR(50),
            vorname VARCHAR(100),
            nachname VARCHAR(100),
            firma VARCHAR(200),
            email VARCHAR(120),
            telefon VARCHAR(50),
            strasse VARCHAR(200),
            plz VARCHAR(10),
            ort VARCHAR(100),
            adresse TEXT,
            mitglied_seit DATE,
            mitgliedschaft_typ VARCHAR(50),
            ist_aktiv BOOLEAN DEFAULT 1,
            notizen TEXT,
            erstellt_am DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. FLASCHEN (mit allen Spalten aus dem Fehler-Log)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flaschen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flasche_nummer VARCHAR(50) UNIQUE NOT NULL,
            externe_flasche_nummer VARCHAR(50),
            barcode VARCHAR(100),
            bauart_zulassung VARCHAR(100),
            seriennummer VARCHAR(100),
            herstellungs_datum DATE,
            interne_flaschennummer_auto VARCHAR(50),
            barcode_typ VARCHAR(20),
            letzte_pruefung_protokoll TEXT,
            pruefung_benachrichtigt BOOLEAN DEFAULT 0,
            pruefung_benachrichtigung_datum DATE,
            flaschen_gewicht_kg DECIMAL(5,2),
            ventil_typ VARCHAR(50),
            ursprungsland VARCHAR(50),
            kaufdatum DATE,
            garantie_bis DATE,
            externe_referenzen TEXT,
            kunde_id INTEGER,
            groesse_liter INTEGER,
            flaschen_typ VARCHAR(50),
            farbe VARCHAR(50),
            hersteller VARCHAR(100),
            pruef_datum DATE,
            naechste_pruefung DATE,
            max_druck_bar INTEGER,
            ist_aktiv BOOLEAN DEFAULT 1,
            ist_zum_fuellen_vorgemerkt BOOLEAN DEFAULT 0,
            letzter_fuellstand INTEGER,
            notizen TEXT,
            erstellt_am DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kunde_id) REFERENCES kunden (id)
        )
    """)
    
    # 3. KOMPRESSOR_BETRIEB (fehlende Tabelle)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kompressor_betrieb (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_zeit DATETIME NOT NULL,
            end_zeit DATETIME,
            betriebsdauer_minuten INTEGER DEFAULT 0,
            oel_getestet BOOLEAN DEFAULT 0,
            oel_test_ergebnis VARCHAR(50),
            oel_tester VARCHAR(100),
            oel_tester_id INTEGER,
            fueller VARCHAR(100),
            fueller_id INTEGER,
            status VARCHAR(50) DEFAULT 'vorbereitung',
            notizen TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 4. BULK_FUELLVORGAENGE (fehlende Tabelle)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bulk_fuellvorgaenge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_zeit DATETIME NOT NULL,
            end_zeit DATETIME,
            gesamtdauer_minuten INTEGER DEFAULT 0,
            operator VARCHAR(100),
            operator_id INTEGER,
            anzahl_flaschen INTEGER DEFAULT 0,
            erfolgreich_gefuellt INTEGER DEFAULT 0,
            fehlgeschlagen INTEGER DEFAULT 0,
            status VARCHAR(50) DEFAULT 'vorbereitung',
            kompressor_betrieb_id INTEGER,
            notizen TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kompressor_betrieb_id) REFERENCES kompressor_betrieb (id)
        )
    """)
    
    # 5. FUELLMANAGER (aus Fehler-Log)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fuellmanager (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            erstellt_am DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) DEFAULT 'offen',
            notizen TEXT
        )
    """)
    
    # 6. USERS (System-Users)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120),
            password_hash VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 7. PATRONEN-Tabellen (aus Fehler-Log)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patronen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            typ VARCHAR(50),
            groesse VARCHAR(50),
            anzahl_verfuegbar INTEGER DEFAULT 0,
            anzahl_reserviert INTEGER DEFAULT 0,
            lagerort VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patrone_lagerbestand (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patrone_id INTEGER,
            anzahl INTEGER DEFAULT 0,
            mindestbestand INTEGER DEFAULT 5,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patrone_id) REFERENCES patronen (id)
        )
    """)
    
    # ============= TEST-DATEN EINFÜGEN =============
    
    print("📊 Füge Test-Daten ein...")
    
    # Test-Kunde
    cursor.execute("""
        INSERT OR IGNORE INTO kunden 
        (mitgliedsnummer, vorname, nachname, email, telefon, ist_aktiv)
        VALUES ('M001', 'Test', 'Kunde', 'test@example.com', '0123456789', 1)
    """)
    
    # Test-Flasche
    cursor.execute("""
        INSERT OR IGNORE INTO flaschen 
        (flasche_nummer, groesse_liter, flaschen_typ, max_druck_bar, ist_aktiv, kunde_id)
        VALUES ('F001', 50, 'Tauchflasche', 300, 1, 1)
    """)
    
    # Test-Kompressor-Betrieb
    cursor.execute("""
        INSERT OR IGNORE INTO kompressor_betrieb
        (start_zeit, status, notizen)
        VALUES (datetime('now'), 'ausgeschaltet', 'System initialisiert')
    """)
    
    # Test-Patronen
    cursor.execute("""
        INSERT OR IGNORE INTO patronen
        (typ, groesse, anzahl_verfuegbar, lagerort)
        VALUES ('CO2', '12g', 100, 'Lager A')
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Vollständige Datenbank erstellt!")
    print(f"📊 Dateigröße: {db_path.stat().st_size} Bytes")
    
    return True

def main():
    print("🔧 WartungsManager - Vollständige Schema-Erstellung")
    print("=" * 60)
    
    try:
        if create_complete_database():
            print("\n🎉 DATENBANK-SCHEMA ERFOLGREICH ERSTELLT!")
            print("=" * 60)
            print("✅ Alle Tabellen mit korrektem Schema erstellt")
            print("✅ Test-Daten eingefügt")
            print("✅ System sollte jetzt fehlerfrei laufen")
            print("\n🚀 Starten Sie den WartungsManager neu:")
            print("python run_production_REPARIERT.py")
        else:
            print("❌ Schema-Erstellung fehlgeschlagen")
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == '__main__':
    main()
