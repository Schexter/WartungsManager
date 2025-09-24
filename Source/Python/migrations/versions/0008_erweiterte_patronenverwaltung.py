# Migration: Erweiterte Patronenverwaltung
# Erstellt: 2025-06-26
# Beschreibung: Neue Models für Patronenvorbereitung, Einkauf und erweiterte Wechsel-Protokolle

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# Revision identifiers
revision = '0008_erweiterte_patronenverwaltung'
down_revision = '0007_kompressor_system'  # Anpassen je nach vorheriger Migration
branch_labels = None
depends_on = None

def upgrade():
    """Erstellt die neuen Tabellen für erweiterte Patronenverwaltung"""
    
    # Tabelle: patrone_vorbereitung
    op.create_table(
        'patrone_vorbereitung',
        sa.Column('id', sa.Integer(), nullable=False),
        
        # Vorbereitung-Info
        sa.Column('vorbereitet_von', sa.String(100), nullable=False),
        sa.Column('vorbereitet_am', sa.DateTime(), nullable=False, default=datetime.utcnow),
        
        # Patronen-Details
        sa.Column('patrone_typ', sa.String(50), nullable=False),
        sa.Column('patrone_nummer', sa.String(20), nullable=True),
        sa.Column('charge_nummer', sa.String(50), nullable=False),
        
        # Gewicht und Qualität
        sa.Column('gewicht_vor_fuellen', sa.Float(), nullable=True),
        sa.Column('gewicht_nach_fuellen', sa.Float(), nullable=True),
        sa.Column('material_verwendet', sa.String(200), nullable=True),
        
        # Status
        sa.Column('ist_bereit', sa.Boolean(), nullable=False, default=True),
        sa.Column('ist_verwendet', sa.Boolean(), nullable=False, default=False),
        sa.Column('verwendung_datum', sa.DateTime(), nullable=True),
        
        # Etikettendruck
        sa.Column('etikett_gedruckt', sa.Boolean(), nullable=False, default=False),
        sa.Column('etikett_gedruckt_am', sa.DateTime(), nullable=True),
        
        # Notizen
        sa.Column('notizen', sa.Text(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Index für bessere Performance
    op.create_index('idx_patrone_vorbereitung_charge', 'patrone_vorbereitung', ['charge_nummer'])
    op.create_index('idx_patrone_vorbereitung_status', 'patrone_vorbereitung', ['ist_bereit', 'ist_verwendet'])
    op.create_index('idx_patrone_vorbereitung_typ', 'patrone_vorbereitung', ['patrone_typ'])

    # Tabelle: patrone_einkauf
    op.create_table(
        'patrone_einkauf',
        sa.Column('id', sa.Integer(), nullable=False),
        
        # Einkauf-Info
        sa.Column('eingekauft_von', sa.String(100), nullable=False),
        sa.Column('einkauf_datum', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('lieferant', sa.String(200), nullable=False),
        
        # Produkt-Details
        sa.Column('produkt_name', sa.String(200), nullable=False),
        sa.Column('produkt_typ', sa.String(50), nullable=False),
        sa.Column('menge', sa.Float(), nullable=False),
        sa.Column('einheit', sa.String(20), nullable=False),
        
        # Preise
        sa.Column('einzelpreis', sa.Float(), nullable=True),
        sa.Column('gesamtpreis', sa.Float(), nullable=True),
        sa.Column('waehrung', sa.String(10), nullable=False, default='EUR'),
        
        # Lieferung
        sa.Column('lieferdatum', sa.DateTime(), nullable=True),
        sa.Column('ist_geliefert', sa.Boolean(), nullable=False, default=False),
        
        # Qualität
        sa.Column('charge_nummer_lieferant', sa.String(100), nullable=True),
        sa.Column('haltbarkeitsdatum', sa.DateTime(), nullable=True),
        sa.Column('qualitaets_zertifikat', sa.String(200), nullable=True),
        
        # Etikettendruck
        sa.Column('kleber_gedruckt', sa.Boolean(), nullable=False, default=False),
        sa.Column('kleber_gedruckt_am', sa.DateTime(), nullable=True),
        
        # Lagerung
        sa.Column('lagerort', sa.String(100), nullable=True),
        sa.Column('verbraucht_menge', sa.Float(), nullable=False, default=0.0),
        sa.Column('verbleibende_menge', sa.Float(), nullable=True),
        
        # Status
        sa.Column('ist_aktiv', sa.Boolean(), nullable=False, default=True),
        sa.Column('notizen', sa.Text(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indices für Einkauf
    op.create_index('idx_patrone_einkauf_lieferant', 'patrone_einkauf', ['lieferant'])
    op.create_index('idx_patrone_einkauf_typ', 'patrone_einkauf', ['produkt_typ'])
    op.create_index('idx_patrone_einkauf_status', 'patrone_einkauf', ['ist_geliefert', 'ist_aktiv'])

    # Tabelle: patrone_wechsel_protokoll
    op.create_table(
        'patrone_wechsel_protokoll',
        sa.Column('id', sa.Integer(), nullable=False),
        
        # Referenz zum ursprünglichen Patronenwechsel
        sa.Column('patronenwechsel_id', sa.Integer(), nullable=False),
        
        # Wechsel-Details
        sa.Column('gewechselt_von', sa.String(100), nullable=False),
        sa.Column('wechsel_datum', sa.DateTime(), nullable=False, default=datetime.utcnow),
        
        # Verwendete vorbereitete Patrone
        sa.Column('vorbereitung_id', sa.Integer(), nullable=True),
        
        # Gewichte beim Wechsel
        sa.Column('alte_patrone_gewicht', sa.Float(), nullable=True),
        sa.Column('neue_patrone_gewicht', sa.Float(), nullable=True),
        
        # Position/Art der Patrone
        sa.Column('position', sa.String(50), nullable=False),
        
        # Zustand
        sa.Column('alte_patrone_zustand', sa.String(200), nullable=True),
        sa.Column('wechsel_grund', sa.String(200), nullable=True),
        
        # Betriebsstunden
        sa.Column('betriebsstunden_alte_patrone', sa.Float(), nullable=True),
        
        # Entsorgung
        sa.Column('alte_patrone_entsorgt', sa.Boolean(), nullable=False, default=False),
        sa.Column('entsorgung_datum', sa.DateTime(), nullable=True),
        sa.Column('entsorgung_art', sa.String(100), nullable=True),
        
        # Notizen
        sa.Column('notizen', sa.Text(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['patronenwechsel_id'], ['patronenwechsel.id'], ),
        sa.ForeignKeyConstraint(['vorbereitung_id'], ['patrone_vorbereitung.id'], )
    )
    
    # Indices für Wechsel-Protokoll
    op.create_index('idx_wechsel_protokoll_patronenwechsel', 'patrone_wechsel_protokoll', ['patronenwechsel_id'])
    op.create_index('idx_wechsel_protokoll_vorbereitung', 'patrone_wechsel_protokoll', ['vorbereitung_id'])
    op.create_index('idx_wechsel_protokoll_position', 'patrone_wechsel_protokoll', ['position'])

def downgrade():
    """Entfernt die erweiterten Patronenverwaltungs-Tabellen"""
    
    # Indices entfernen
    op.drop_index('idx_wechsel_protokoll_position', table_name='patrone_wechsel_protokoll')
    op.drop_index('idx_wechsel_protokoll_vorbereitung', table_name='patrone_wechsel_protokoll')
    op.drop_index('idx_wechsel_protokoll_patronenwechsel', table_name='patrone_wechsel_protokoll')
    
    op.drop_index('idx_patrone_einkauf_status', table_name='patrone_einkauf')
    op.drop_index('idx_patrone_einkauf_typ', table_name='patrone_einkauf')
    op.drop_index('idx_patrone_einkauf_lieferant', table_name='patrone_einkauf')
    
    op.drop_index('idx_patrone_vorbereitung_typ', table_name='patrone_vorbereitung')
    op.drop_index('idx_patrone_vorbereitung_status', table_name='patrone_vorbereitung')
    op.drop_index('idx_patrone_vorbereitung_charge', table_name='patrone_vorbereitung')
    
    # Tabellen entfernen
    op.drop_table('patrone_wechsel_protokoll')
    op.drop_table('patrone_einkauf')
    op.drop_table('patrone_vorbereitung')
