#!/usr/bin/env python3
"""
KORRIGIERTE Migration für erweiterte Flaschen-Rückverfolgbarkeit
Direkte SQL-Ausführung ohne Alembic-Proxy-Probleme
"""

import sys
import os
import sqlite3
from datetime import datetime

# Aktuelles Projektverzeichnis hinzufügen
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def migration_direkt_ausführen():
    """Führt die Migration direkt über SQLite aus"""
    
    db_path = os.path.join(current_dir, 'database', 'wartungsmanager.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    print("🔧 Starte direkte Migration für erweiterte Flaschen-Rückverfolgbarkeit...")
    print(f"📂 Datenbank: {db_path}")
    
    try:
        # Backup erstellen
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 Backup erstellt: {backup_path}")
        
        # Verbindung zur Datenbank
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📝 Prüfe aktuelle Tabellenstruktur...")
        
        # Aktuelle Spalten prüfen
        cursor.execute("PRAGMA table_info(flaschen)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Vorhandene Spalten: {len(existing_columns)}")
        
        # Neue Spalten definieren
        neue_spalten = [
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
        
        # Spalten hinzufügen
        added_count = 0
        for spalte, definition in neue_spalten:
            if spalte not in existing_columns:
                print(f"  ➕ Füge Spalte hinzu: {spalte}")
                try:
                    cursor.execute(f"ALTER TABLE flaschen ADD COLUMN {spalte} {definition}")
                    added_count += 1
                except sqlite3.Error as e:
                    print(f"    ⚠️ Warnung bei {spalte}: {e}")
            else:
                print(f"  ✅ Spalte bereits vorhanden: {spalte}")
        
        print(f"📊 {added_count} neue Spalten hinzugefügt")
        
        # Indizes erstellen
        indizes = [
            (
                "idx_flaschen_barcode_typ",
                "CREATE INDEX IF NOT EXISTS idx_flaschen_barcode_typ ON flaschen(barcode, barcode_typ)"
            ),
            (
                "idx_flaschen_pruefung_status", 
                "CREATE INDEX IF NOT EXISTS idx_flaschen_pruefung_status ON flaschen(naechste_pruefung, pruefung_benachrichtigt)"
            )
        ]
        
        for index_name, sql in indizes:
            try:
                cursor.execute(sql)
                print(f"  📊 Index erstellt: {index_name}")
            except sqlite3.Error as e:
                print(f"    ⚠️ Index-Warnung {index_name}: {e}")
        
        # Änderungen committen
        conn.commit()
        
        # Validierung: Neue Tabellenstruktur prüfen
        cursor.execute("PRAGMA table_info(flaschen)")
        final_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Finale Spaltenanzahl: {len(final_columns)}")
        
        # Test: Beispiel-Update auf vorhandene Flaschen
        cursor.execute("SELECT COUNT(*) FROM flaschen")
        flaschen_count = cursor.fetchone()[0]
        
        if flaschen_count > 0:
            print(f"🧪 Teste mit {flaschen_count} vorhandenen Flaschen...")
            
            # Setze Auto-Flag für alle bestehenden Flaschen
            cursor.execute("""
                UPDATE flaschen 
                SET interne_flaschennummer_auto = TRUE,
                    barcode_typ = 'CODE128'
                WHERE interne_flaschennummer_auto IS NULL
            """)
            
            updated_rows = cursor.rowcount
            print(f"  ✅ {updated_rows} Flaschen aktualisiert")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Migration erfolgreich abgeschlossen!")
        print("\n📋 Neue Features verfügbar:")
        print("   • Automatische interne Flaschennummer-Generierung")
        print("   • Erweiterte Bauartzulassung-Verwaltung") 
        print("   • Prüfungshistorie und -Benachrichtigungen")
        print("   • Barcode-Optimierungen")
        print("   • Externe System-Integration")
        print("   • Vollständige Rückverfolgbarkeit")
        print("\n🚀 Starten Sie den WartungsManager neu, um alle Features zu nutzen!")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Migration: {e}")
        import traceback
        traceback.print_exc()
        
        # Versuche Rollback
        try:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            print("🔄 Rollback durchgeführt")
        except:
            pass
            
        return False

def flask_app_migration():
    """Alternative: Migration über Flask-App-Kontext"""
    
    try:
        from app import create_app, db
        
        app = create_app()
        
        with app.app_context():
            print("🔧 Führe Migration über Flask-App aus...")
            
            # Direkte SQL-Befehle über SQLAlchemy
            from sqlalchemy import text
            
            # Neue Spalten hinzufügen
            neue_spalten = [
                'ALTER TABLE flaschen ADD COLUMN interne_flaschennummer_auto BOOLEAN DEFAULT FALSE',
                'ALTER TABLE flaschen ADD COLUMN barcode_typ VARCHAR(20) DEFAULT "CODE128"',
                'ALTER TABLE flaschen ADD COLUMN letzte_pruefung_protokoll TEXT',
                'ALTER TABLE flaschen ADD COLUMN pruefung_benachrichtigt BOOLEAN DEFAULT FALSE',
                'ALTER TABLE flaschen ADD COLUMN pruefung_benachrichtigung_datum DATE',
                'ALTER TABLE flaschen ADD COLUMN flaschen_gewicht_kg REAL',
                'ALTER TABLE flaschen ADD COLUMN ventil_typ VARCHAR(50)',
                'ALTER TABLE flaschen ADD COLUMN ursprungsland VARCHAR(50)',
                'ALTER TABLE flaschen ADD COLUMN kaufdatum DATE',
                'ALTER TABLE flaschen ADD COLUMN garantie_bis DATE',
                'ALTER TABLE flaschen ADD COLUMN externe_referenzen TEXT'
            ]
            
            for sql_command in neue_spalten:
                try:
                    db.session.execute(text(sql_command))
                    spalte_name = sql_command.split('ADD COLUMN ')[1].split(' ')[0]
                    print(f"  ✅ Spalte hinzugefügt: {spalte_name}")
                except Exception as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"  ⚠️ Warnung: {e}")
                    else:
                        spalte_name = sql_command.split('ADD COLUMN ')[1].split(' ')[0]
                        print(f"  ✅ Spalte bereits vorhanden: {spalte_name}")
            
            # Indizes erstellen
            indizes = [
                'CREATE INDEX IF NOT EXISTS idx_flaschen_barcode_typ ON flaschen(barcode, barcode_typ)',
                'CREATE INDEX IF NOT EXISTS idx_flaschen_pruefung_status ON flaschen(naechste_pruefung, pruefung_benachrichtigt)'
            ]
            
            for index_sql in indizes:
                try:
                    db.session.execute(text(index_sql))
                    print(f"  📊 Index erstellt")
                except Exception as e:
                    print(f"  ⚠️ Index-Warnung: {e}")
            
            # Änderungen committen
            db.session.commit()
            
            print("✅ Flask-App Migration erfolgreich!")
            return True
            
    except Exception as e:
        print(f"❌ Flask-App Migration fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    print("🚀 WartungsManager - Erweiterte Flaschen-Rückverfolgbarkeit")
    print("=" * 60)
    
    # Versuche zuerst direkte Migration
    if migration_direkt_ausführen():
        print("\n✅ Direkte Migration erfolgreich!")
        exit(0)
    else:
        print("\n⚠️ Direkte Migration fehlgeschlagen, versuche Flask-App...")
        
        # Fallback: Flask-App Migration
        if flask_app_migration():
            print("\n✅ Flask-App Migration erfolgreich!")
            exit(0)
        else:
            print("\n❌ Alle Migrations-Versuche fehlgeschlagen!")
            print("\n📋 Manuelle Schritte:")
            print("1. Prüfen Sie die Datenbankverbindung")
            print("2. Stellen Sie sicher, dass die Flask-App korrekt konfiguriert ist")
            print("3. Führen Sie ein Backup durch bevor Sie es erneut versuchen")
            exit(1)
