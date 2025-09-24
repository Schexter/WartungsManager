# Migration für 2-stufigen Flaschen-Workflow
# 
# 1. FLASCHEN ANNEHMEN → Warteliste (Kompressor AUS/AN egal)
# 2. FLASCHEN FÜLLEN → Aus Warteliste (Kompressor muss AN)

"""Neue Warteliste für 2-stufigen Workflow

Revision ID: 0009_warteliste_workflow
Revises: 0008_erweiterte_patronenverwaltung
Create Date: 2025-07-02 17:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '0009_warteliste_workflow'
down_revision = '0008_erweiterte_patronenverwaltung'
branch_labels = None
depends_on = None

def upgrade():
    """Upgrade Database Schema"""
    
    # 1. Warteliste-Einträge Tabelle
    op.create_table('warteliste_eintraege',
        sa.Column('id', sa.Integer, primary_key=True),
        
        # Beziehungen
        sa.Column('flasche_id', sa.Integer, sa.ForeignKey('flaschen.id'), nullable=False),
        
        # Annahme-Daten
        sa.Column('annahme_datum', sa.Date, nullable=False),
        sa.Column('gewuenschter_druck', sa.Integer, nullable=False),
        sa.Column('besonderheiten', sa.Text),
        sa.Column('prioritaet', sa.String(20), default='normal'),  # hoch, normal, niedrig
        
        # Status-Tracking
        sa.Column('status', sa.String(30), default='wartend'),  # wartend, wird_gefuellt, gefuellt, abgebrochen
        
        # Füll-Prozess
        sa.Column('fueller', sa.String(100)),
        sa.Column('luftgemisch', sa.String(50)),
        sa.Column('fuell_start', sa.DateTime),
        sa.Column('fuell_ende', sa.DateTime),
        sa.Column('erreichter_druck', sa.Integer),
        
        # Meta-Daten
        sa.Column('notizen', sa.Text),
        sa.Column('erstellt_am', sa.DateTime, default=sa.func.now()),
        sa.Column('aktualisiert_am', sa.DateTime, default=sa.func.now())
    )
    
    # Indizes für Performance
    op.create_index('idx_warteliste_status', 'warteliste_eintraege', ['status'])
    op.create_index('idx_warteliste_annahme', 'warteliste_eintraege', ['annahme_datum'])
    op.create_index('idx_warteliste_prioritaet', 'warteliste_eintraege', ['prioritaet'])
    op.create_index('idx_warteliste_flasche', 'warteliste_eintraege', ['flasche_id'])
    
    # 2. Flaschen-Tabelle aktualisieren (falls Spalten fehlen)
    try:
        # Prüfe ob Spalten existieren und füge sie hinzu falls nötig
        op.add_column('flaschen', sa.Column('barcode', sa.String(100), unique=True))
        op.add_column('flaschen', sa.Column('flasche_nummer', sa.String(50)))
        op.add_column('flaschen', sa.Column('erstellt_am', sa.DateTime, default=sa.func.now()))
    except:
        # Spalten existieren bereits
        pass
    
    # 3. Kunden-Tabelle aktualisieren (falls Spalten fehlen) 
    try:
        op.add_column('kunden', sa.Column('adresse', sa.Text))
        op.add_column('kunden', sa.Column('erstellt_am', sa.DateTime, default=sa.func.now()))
    except:
        # Spalten existieren bereits
        pass

def downgrade():
    """Downgrade Database Schema"""
    
    # Indizes entfernen
    op.drop_index('idx_warteliste_flasche')
    op.drop_index('idx_warteliste_prioritaet')
    op.drop_index('idx_warteliste_annahme')
    op.drop_index('idx_warteliste_status')
    
    # Tabelle entfernen
    op.drop_table('warteliste_eintraege')
    
    # Spalten aus anderen Tabellen entfernen (optional)
    # Vorsicht: Kann Datenverlust verursachen
    try:
        op.drop_column('flaschen', 'barcode')
        op.drop_column('flaschen', 'flasche_nummer')
        op.drop_column('flaschen', 'erstellt_am')
    except:
        pass
    
    try:
        op.drop_column('kunden', 'adresse')
        op.drop_column('kunden', 'erstellt_am')
    except:
        pass
