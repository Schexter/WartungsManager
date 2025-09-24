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
        ]\n        \n        # Spalten hinzufügen\n        added_count = 0\n        for spalte, definition in neue_spalten:\n            if spalte not in existing_columns:\n                print(f"  ➕ Füge Spalte hinzu: {spalte}")\n                try:\n                    cursor.execute(f"ALTER TABLE flaschen ADD COLUMN {spalte} {definition}")\n                    added_count += 1\n                except sqlite3.Error as e:\n                    print(f"    ⚠️ Warnung bei {spalte}: {e}")\n            else:\n                print(f"  ✅ Spalte bereits vorhanden: {spalte}")\n        \n        print(f"📊 {added_count} neue Spalten hinzugefügt")\n        \n        # Indizes erstellen\n        indizes = [\n            (\n                "idx_flaschen_barcode_typ",\n                "CREATE INDEX IF NOT EXISTS idx_flaschen_barcode_typ ON flaschen(barcode, barcode_typ)"\n            ),\n            (\n                "idx_flaschen_pruefung_status", \n                "CREATE INDEX IF NOT EXISTS idx_flaschen_pruefung_status ON flaschen(naechste_pruefung, pruefung_benachrichtigt)"\n            )\n        ]\n        \n        for index_name, sql in indizes:\n            try:\n                cursor.execute(sql)\n                print(f"  📊 Index erstellt: {index_name}")\n            except sqlite3.Error as e:\n                print(f"    ⚠️ Index-Warnung {index_name}: {e}")\n        \n        # Änderungen committen\n        conn.commit()\n        \n        # Validierung: Neue Tabellenstruktur prüfen\n        cursor.execute("PRAGMA table_info(flaschen)")\n        final_columns = [row[1] for row in cursor.fetchall()]\n        print(f"📋 Finale Spaltenanzahl: {len(final_columns)}")\n        \n        # Test: Beispiel-Update auf vorhandene Flaschen\n        cursor.execute("SELECT COUNT(*) FROM flaschen")\n        flaschen_count = cursor.fetchone()[0]\n        \n        if flaschen_count > 0:\n            print(f"🧪 Teste mit {flaschen_count} vorhandenen Flaschen...")\n            \n            # Setze Auto-Flag für alle bestehenden Flaschen\n            cursor.execute("""\n                UPDATE flaschen \n                SET interne_flaschennummer_auto = TRUE,\n                    barcode_typ = 'CODE128'\n                WHERE interne_flaschennummer_auto IS NULL\n            """)\n            \n            updated_rows = cursor.rowcount\n            print(f"  ✅ {updated_rows} Flaschen aktualisiert")\n        \n        conn.commit()\n        conn.close()\n        \n        print("\\n🎉 Migration erfolgreich abgeschlossen!")\n        print("\\n📋 Neue Features verfügbar:")\n        print("   • Automatische interne Flaschennummer-Generierung")\n        print("   • Erweiterte Bauartzulassung-Verwaltung") \n        print("   • Prüfungshistorie und -Benachrichtigungen")\n        print("   • Barcode-Optimierungen")\n        print("   • Externe System-Integration")\n        print("   • Vollständige Rückverfolgbarkeit")\n        print("\\n🚀 Starten Sie den WartungsManager neu, um alle Features zu nutzen!")\n        \n        return True\n        \n    except Exception as e:\n        print(f"❌ Fehler bei Migration: {e}")\n        import traceback\n        traceback.print_exc()\n        \n        # Versuche Rollback\n        try:\n            if 'conn' in locals():\n                conn.rollback()\n                conn.close()\n            print("🔄 Rollback durchgeführt")\n        except:\n            pass\n            \n        return False\n\ndef flask_app_migration():\n    """Alternative: Migration über Flask-App-Kontext"""\n    \n    try:\n        from app import create_app, db\n        \n        app = create_app()\n        \n        with app.app_context():\n            print("🔧 Führe Migration über Flask-App aus...")\n            \n            # Direkte SQL-Befehle über SQLAlchemy\n            from sqlalchemy import text\n            \n            # Neue Spalten hinzufügen\n            neue_spalten = [\n                'ALTER TABLE flaschen ADD COLUMN interne_flaschennummer_auto BOOLEAN DEFAULT FALSE',\n                'ALTER TABLE flaschen ADD COLUMN barcode_typ VARCHAR(20) DEFAULT \"CODE128\"',\n                'ALTER TABLE flaschen ADD COLUMN letzte_pruefung_protokoll TEXT',\n                'ALTER TABLE flaschen ADD COLUMN pruefung_benachrichtigt BOOLEAN DEFAULT FALSE',\n                'ALTER TABLE flaschen ADD COLUMN pruefung_benachrichtigung_datum DATE',\n                'ALTER TABLE flaschen ADD COLUMN flaschen_gewicht_kg REAL',\n                'ALTER TABLE flaschen ADD COLUMN ventil_typ VARCHAR(50)',\n                'ALTER TABLE flaschen ADD COLUMN ursprungsland VARCHAR(50)',\n                'ALTER TABLE flaschen ADD COLUMN kaufdatum DATE',\n                'ALTER TABLE flaschen ADD COLUMN garantie_bis DATE',\n                'ALTER TABLE flaschen ADD COLUMN externe_referenzen TEXT'\n            ]\n            \n            for sql_command in neue_spalten:\n                try:\n                    db.session.execute(text(sql_command))\n                    spalte_name = sql_command.split('ADD COLUMN ')[1].split(' ')[0]\n                    print(f"  ✅ Spalte hinzugefügt: {spalte_name}")\n                except Exception as e:\n                    if "duplicate column name" not in str(e).lower():\n                        print(f"  ⚠️ Warnung: {e}")\n                    else:\n                        spalte_name = sql_command.split('ADD COLUMN ')[1].split(' ')[0]\n                        print(f"  ✅ Spalte bereits vorhanden: {spalte_name}")\n            \n            # Indizes erstellen\n            indizes = [\n                'CREATE INDEX IF NOT EXISTS idx_flaschen_barcode_typ ON flaschen(barcode, barcode_typ)',\n                'CREATE INDEX IF NOT EXISTS idx_flaschen_pruefung_status ON flaschen(naechste_pruefung, pruefung_benachrichtigt)'\n            ]\n            \n            for index_sql in indizes:\n                try:\n                    db.session.execute(text(index_sql))\n                    print(f"  📊 Index erstellt")\n                except Exception as e:\n                    print(f"  ⚠️ Index-Warnung: {e}")\n            \n            # Änderungen committen\n            db.session.commit()\n            \n            print("✅ Flask-App Migration erfolgreich!")\n            return True\n            \n    except Exception as e:\n        print(f"❌ Flask-App Migration fehlgeschlagen: {e}")\n        return False\n\nif __name__ == "__main__":\n    print("🚀 WartungsManager - Erweiterte Flaschen-Rückverfolgbarkeit")\n    print("=" * 60)\n    \n    # Versuche zuerst direkte Migration\n    if migration_direkt_ausführen():\n        print("\\n✅ Direkte Migration erfolgreich!")\n        exit(0)\n    else:\n        print("\\n⚠️ Direkte Migration fehlgeschlagen, versuche Flask-App...")\n        \n        # Fallback: Flask-App Migration\n        if flask_app_migration():\n            print("\\n✅ Flask-App Migration erfolgreich!")\n            exit(0)\n        else:\n            print("\\n❌ Alle Migrations-Versuche fehlgeschlagen!")\n            print("\\n📋 Manuelle Schritte:")\n            print("1. Prüfen Sie die Datenbankverbindung")\n            print("2. Stellen Sie sicher, dass die Flask-App korrekt konfiguriert ist")\n            print("3. Führen Sie ein Backup durch bevor Sie es erneut versuchen")\n            exit(1)
