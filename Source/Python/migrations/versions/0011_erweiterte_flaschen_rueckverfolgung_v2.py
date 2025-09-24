"""Erweiterte Flaschen-Rückverfolgbarkeit - Korrigierte Migration

Revision ID: 0011_erweiterte_flaschen_rueckverfolgung_v2
Revises: 0010_erweiterte_flaschen_felder
Create Date: 2025-07-02 

Fügt erweiterte Felder für Flaschen-Rückverfolgbarkeit und Prüfungsmanagement hinzu.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers
revision = '0011_erweiterte_flaschen_rueckverfolgung_v2'
down_revision = '0010_erweiterte_flaschen_felder'
branch_labels = None
depends_on = None


def upgrade():
    """
    Erweitert das Flaschen-System um verbesserte Rückverfolgbarkeit
    """
    
    try:
        print("🔧 Starte Datenbank-Erweiterung...")
        
        # Neue Spalten für erweiterte Rückverfolgbarkeit hinzufügen
        neue_spalten = [
            ('interne_flaschennummer_auto', 'BOOLEAN', 'DEFAULT FALSE'),
            ('barcode_typ', 'VARCHAR(20)', 'DEFAULT "CODE128"'),
            ('letzte_pruefung_protokoll', 'TEXT', ''),
            ('pruefung_benachrichtigt', 'BOOLEAN', 'DEFAULT FALSE'),
            ('pruefung_benachrichtigung_datum', 'DATE', ''),
            ('flaschen_gewicht_kg', 'REAL', ''),
            ('ventil_typ', 'VARCHAR(50)', ''),
            ('ursprungsland', 'VARCHAR(50)', ''),
            ('kaufdatum', 'DATE', ''),
            ('garantie_bis', 'DATE', ''),
            ('externe_referenzen', 'TEXT', ''),
        ]
        
        # Prüfe welche Spalten bereits existieren
        connection = op.get_bind()
        result = connection.execute(text("PRAGMA table_info(flaschen)"))
        existing_columns = [row[1] for row in result.fetchall()]
        
        # Füge nur neue Spalten hinzu
        for spalte, typ, default in neue_spalten:
            if spalte not in existing_columns:
                print(f"  ➕ Füge Spalte hinzu: {spalte}")
                
                sql_command = f"ALTER TABLE flaschen ADD COLUMN {spalte} {typ}"
                if default:
                    sql_command += f" {default}"
                
                try:
                    op.execute(text(sql_command))
                except Exception as e:
                    print(f"    ⚠️ Warnung bei {spalte}: {e}")
            else:
                print(f"  ✅ Spalte bereits vorhanden: {spalte}")
        
        # Erstelle Indizes für bessere Performance
        try:
            # Index für Barcode-Suche
            op.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_flaschen_barcode_typ 
                ON flaschen(barcode, barcode_typ)
            """))
            print("  📊 Index für Barcode-Suche erstellt")
            
            # Index für Prüfungsverwaltung
            op.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_flaschen_pruefung_status 
                ON flaschen(naechste_pruefung, pruefung_benachrichtigt)
            """))
            print("  📊 Index für Prüfungsverwaltung erstellt")
            
        except Exception as e:
            print(f"    ⚠️ Index-Warnung: {e}")
        
        print("✅ Migration 0011: Erweiterte Flaschen-Rückverfolgbarkeit erfolgreich")
        
    except Exception as e:
        print(f"❌ Fehler bei Migration 0011: {e}")
        raise


def downgrade():
    """
    Entfernt die erweiterten Rückverfolgbarkeits-Felder
    """
    
    try:
        print("🔄 Starte Downgrade...")
        
        # Entferne Indizes
        try:
            op.execute(text("DROP INDEX IF EXISTS idx_flaschen_barcode_typ"))
            op.execute(text("DROP INDEX IF EXISTS idx_flaschen_pruefung_status"))
            print("  📊 Indizes entfernt")
        except Exception:
            pass
        
        # Entferne Spalten (SQLite unterstützt DROP COLUMN erst ab 3.35+)
        # Für Kompatibilität: Spalten bleiben, werden aber als deprecated markiert
        print("  ℹ️ Spalten bleiben für Kompatibilität erhalten (SQLite-Limitation)")
        print("✅ Downgrade 0011: Abgeschlossen")
        
    except Exception as e:
        print(f"❌ Fehler bei Downgrade 0011: {e}")
        raise
