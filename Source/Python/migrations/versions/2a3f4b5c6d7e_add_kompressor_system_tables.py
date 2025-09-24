"""Add Kompressor System Tables

Revision ID: 2a3f4b5c6d7e
Revises: 04ecc7d05779
Create Date: 2025-06-26 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '2a3f4b5c6d7e'
down_revision = '04ecc7d05779'
branch_labels = None
depends_on = None


def upgrade():
    # Create kunden table
    op.create_table('kunden',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mitgliedsnummer', sa.String(length=20), nullable=True),
        sa.Column('vorname', sa.String(length=100), nullable=False),
        sa.Column('nachname', sa.String(length=100), nullable=False),
        sa.Column('firma', sa.String(length=200), nullable=True),
        sa.Column('email', sa.String(length=150), nullable=True),
        sa.Column('telefon', sa.String(length=30), nullable=True),
        sa.Column('strasse', sa.String(length=200), nullable=True),
        sa.Column('plz', sa.String(length=10), nullable=True),
        sa.Column('ort', sa.String(length=100), nullable=True),
        sa.Column('land', sa.String(length=50), nullable=True),
        sa.Column('geburtsdatum', sa.Date(), nullable=True),
        sa.Column('mitgliedschaft_typ', sa.String(length=50), nullable=True),
        sa.Column('mitgliedschaft_start', sa.Date(), nullable=True),
        sa.Column('mitgliedschaft_ende', sa.Date(), nullable=True),
        sa.Column('notizen', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('mitgliedsnummer')
    )
    
    # Create kompressor_betrieb table
    op.create_table('kompressor_betrieb',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('start_zeit', sa.DateTime(), nullable=False),
        sa.Column('end_zeit', sa.DateTime(), nullable=True),
        sa.Column('betriebsdauer_minuten', sa.Integer(), nullable=True),
        sa.Column('oel_getestet', sa.Boolean(), nullable=False),
        sa.Column('oel_test_ergebnis', sa.String(length=10), nullable=True),
        sa.Column('oel_tester', sa.String(length=100), nullable=True),
        sa.Column('oel_tester_id', sa.Integer(), nullable=True),
        sa.Column('fueller', sa.String(length=100), nullable=False),
        sa.Column('fueller_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('notizen', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fueller_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['oel_tester_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create flaschen table
    op.create_table('flaschen',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seriennummer', sa.String(length=50), nullable=False),
        sa.Column('flaschennummer', sa.String(length=50), nullable=True),
        sa.Column('kunde_id', sa.Integer(), nullable=False),
        sa.Column('groesse_liter', sa.Float(), nullable=False),
        sa.Column('flaschen_typ', sa.String(length=50), nullable=True),
        sa.Column('farbe', sa.String(length=30), nullable=True),
        sa.Column('hersteller', sa.String(length=100), nullable=True),
        sa.Column('herstellungsjahr', sa.Integer(), nullable=True),
        sa.Column('max_druck_bar', sa.Integer(), nullable=True),
        sa.Column('letztes_pruef_datum', sa.Date(), nullable=True),
        sa.Column('naechste_pruefung', sa.Date(), nullable=True),
        sa.Column('tuv_pruefstelle', sa.String(length=100), nullable=True),
        sa.Column('notizen', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('vorgemerkt', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['kunde_id'], ['kunden.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('seriennummer')
    )
    
    # Create bulk_fuellvorgaenge table
    op.create_table('bulk_fuellvorgaenge',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('start_zeit', sa.DateTime(), nullable=False),
        sa.Column('end_zeit', sa.DateTime(), nullable=True),
        sa.Column('operator', sa.String(length=100), nullable=False),
        sa.Column('operator_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('anzahl_flaschen', sa.Integer(), nullable=True),
        sa.Column('flaschen_gefuellt', sa.Integer(), nullable=True),
        sa.Column('flaschen_fehlgeschlagen', sa.Integer(), nullable=True),
        sa.Column('notizen', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create flasche_fuellvorgang table (many-to-many with additional columns)
    op.create_table('flasche_fuellvorgang',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bulk_vorgang_id', sa.Integer(), nullable=False),
        sa.Column('flasche_id', sa.Integer(), nullable=False),
        sa.Column('ziel_druck', sa.Integer(), nullable=False),
        sa.Column('erreicher_druck', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('start_zeit', sa.DateTime(), nullable=True),
        sa.Column('end_zeit', sa.DateTime(), nullable=True),
        sa.Column('grund', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['bulk_vorgang_id'], ['bulk_fuellvorgaenge.id'], ),
        sa.ForeignKeyConstraint(['flasche_id'], ['flaschen.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Insert sample data
    insert_sample_data()


def insert_sample_data():
    """Insert sample data for testing"""
    
    # Sample customer
    kunden_table = sa.table('kunden',
        sa.column('mitgliedsnummer', sa.String),
        sa.column('vorname', sa.String),
        sa.column('nachname', sa.String),
        sa.column('email', sa.String),
        sa.column('telefon', sa.String),
        sa.column('mitgliedschaft_typ', sa.String),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime)
    )
    
    op.bulk_insert(kunden_table, [
        {
            'mitgliedsnummer': 'M-001',
            'vorname': 'Max',
            'nachname': 'Mustermann',
            'email': 'max@beispiel.de',
            'telefon': '0123-456789',
            'mitgliedschaft_typ': 'Standard',
            'is_active': True,
            'created_at': datetime.utcnow()
        }
    ])


def downgrade():
    # Drop tables in reverse order due to foreign keys
    op.drop_table('flasche_fuellvorgang')
    op.drop_table('bulk_fuellvorgaenge')
    op.drop_table('flaschen')
    op.drop_table('kompressor_betrieb')
    op.drop_table('kunden')
