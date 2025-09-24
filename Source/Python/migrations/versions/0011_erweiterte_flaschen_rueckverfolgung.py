"""Erweiterte Flaschen-Rückverfolgbarkeit

Revision ID: 0011_erweiterte_flaschen_rueckverfolgung
Revises: 0010_erweiterte_flaschen_felder
Create Date: 2025-07-02 

Fügt erweiterte Felder für Flaschen-Rückverfolgbarkeit und Prüfungsmanagement hinzu:
- Interne Flaschennummer-Generierung
- Erweiterte Bauartzulassung-Verwaltung
- Prüfungshistorie und -Benachrichtigungen
- Barcode-Optimierungen
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = '0011_erweiterte_flaschen_rueckverfolgung'
down_revision = '0010_erweiterte_flaschen_felder'
branch_labels = None
depends_on = None


def upgrade():
    """
    Erweitert das Flaschen-System um verbesserte Rückverfolgbarkeit
    """
    
    try:
        # Prüfen ob Spalten bereits existieren
        inspector = sa.inspect(op.get_bind())
        columns = [col['name'] for col in inspector.get_columns('flaschen')]
        
        # Neue optionale Felder für erweiterte Rückverfolgbarkeit
        new_columns = [
            ('interne_flaschennummer_auto', sa.Boolean, False),  # Automatische Generierung
            ('barcode_typ', sa.String(20), 'CODE128'),  # Barcode-Format
            ('letzte_pruefung_protokoll', sa.Text, None),  # Prüfungsprotokoll
            ('pruefung_benachrichtigt', sa.Boolean, False),  # Benachrichtigung gesendet
            ('pruefung_benachrichtigung_datum', sa.Date, None),  # Wann benachrichtigt
            ('flaschen_gewicht_kg', sa.Float, None),  # Eigengewicht
            ('ventil_typ', sa.String(50), None),  # Ventiltyp
            ('ursprungsland', sa.String(50), None),  # Herstellungsland
            ('kaufdatum', sa.Date, None),  # Kaufdatum
            ('garantie_bis', sa.Date, None),  # Garantieende
            ('externe_referenzen', sa.Text, None),  # JSON für externe Systeme
        ]
        
        # Füge nur neue Spalten hinzu
        for col_name, col_type, default_value in new_columns:
            if col_name not in columns:
                print(f"Füge Spalte hinzu: {col_name}")
                
                if isinstance(col_type, type) and issubclass(col_type, sa.Boolean):
                    op.add_column('flaschen', 
                        sa.Column(col_name, col_type, nullable=True, default=default_value))
                elif isinstance(col_type, type) and issubclass(col_type, sa.Float):
                    op.add_column('flaschen', 
                        sa.Column(col_name, col_type, nullable=True))
                elif isinstance(col_type, type) and issubclass(col_type, sa.Date):
                    op.add_column('flaschen', 
                        sa.Column(col_name, col_type, nullable=True))
                else:
                    op.add_column('flaschen', 
                        sa.Column(col_name, col_type, nullable=True))
            else:
                print(f"Spalte bereits vorhanden: {col_name}")
        
        # Index für bessere Performance bei Barcode-Suche
        try:
            op.create_index('idx_flaschen_barcode_typ', 'flaschen', ['barcode', 'barcode_typ'])
        except Exception as e:
            print(f"Index bereits vorhanden oder Fehler: {e}")
        
        # Index für Prüfungsverwaltung
        try:
            op.create_index('idx_flaschen_pruefung_status', 'flaschen', 
                          ['naechste_pruefung', 'pruefung_benachrichtigt'])
        except Exception as e:
            print(f"Index bereits vorhanden oder Fehler: {e}")
        
        print("✅ Migration 0011: Erweiterte Flaschen-Rückverfolgbarkeit erfolgreich")
        
    except Exception as e:
        print(f"❌ Fehler bei Migration 0011: {e}")
        raise


def downgrade():
    """
    Entfernt die erweiterten Rückverfolgbarkeits-Felder
    """
    
    try:
        # Entferne Indizes
        try:
            op.drop_index('idx_flaschen_barcode_typ', 'flaschen')
            op.drop_index('idx_flaschen_pruefung_status', 'flaschen')
        except Exception:
            pass
        
        # Entferne Spalten
        columns_to_remove = [
            'interne_flaschennummer_auto',
            'barcode_typ',
            'letzte_pruefung_protokoll',
            'pruefung_benachrichtigt',
            'pruefung_benachrichtigung_datum',
            'flaschen_gewicht_kg',
            'ventil_typ',
            'ursprungsland',
            'kaufdatum',
            'garantie_bis',
            'externe_referenzen'
        ]
        
        for col_name in columns_to_remove:
            try:
                op.drop_column('flaschen', col_name)
            except Exception as e:
                print(f"Spalte {col_name} konnte nicht entfernt werden: {e}")
        
        print("✅ Downgrade 0011: Erweiterte Felder entfernt")
        
    except Exception as e:
        print(f"❌ Fehler bei Downgrade 0011: {e}")
        raise
