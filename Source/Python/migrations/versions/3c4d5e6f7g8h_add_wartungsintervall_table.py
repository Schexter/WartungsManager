"""Add wartungsintervall table

Revision ID: 3c4d5e6f7g8h
Revises: 2a3f4b5c6d7e
Create Date: 2025-06-26 12:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '3c4d5e6f7g8h'
down_revision = '2a3f4b5c6d7e'
branch_labels = None
depends_on = None

def upgrade():
    # Create wartungsintervall table
    op.create_table(
        'wartungsintervall',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('start_datum', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('reset_grund', sa.String(length=200), nullable=True),
        sa.Column('startstand_stunden', sa.Float(), nullable=False, default=0.0),
        sa.Column('wartungsintervall_stunden', sa.Float(), nullable=False, default=100.0),
        sa.Column('naechste_wartung_bei', sa.Float(), nullable=True),
        sa.Column('ist_aktiv', sa.Boolean(), nullable=False, default=True),
        sa.Column('durchgefuehrt_von', sa.String(length=100), nullable=True),
        sa.Column('notizen', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Drop wartungsintervall table
    op.drop_table('wartungsintervall')
