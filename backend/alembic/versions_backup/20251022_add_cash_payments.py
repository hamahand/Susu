"""add cash payment support

Revision ID: 20251022_cash_payments
Revises: 20251022_payment_prefs
Create Date: 2025-10-22 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251022_cash_payments'
down_revision = '20251022_payment_prefs'
branch_labels = None
depends_on = None


def upgrade():
    # Add payment_type column to payments table
    op.add_column('payments', 
        sa.Column('payment_type', sa.String(length=20), nullable=False, server_default='momo')
    )
    
    # Add marked_paid_by column to payments table (for cash payments)
    op.add_column('payments',
        sa.Column('marked_paid_by', sa.Integer(), nullable=True)
    )
    
    # Add foreign key constraint for marked_paid_by
    op.create_foreign_key(
        'fk_payments_marked_paid_by',
        'payments', 'users',
        ['marked_paid_by'], ['id'],
        ondelete='SET NULL'
    )
    
    # Add cash_only column to groups table
    op.add_column('groups',
        sa.Column('cash_only', sa.Boolean(), nullable=False, server_default='false')
    )
    
    # Create index on payment_type for analytics
    op.create_index('ix_payments_payment_type', 'payments', ['payment_type'])


def downgrade():
    # Drop index
    op.drop_index('ix_payments_payment_type', table_name='payments')
    
    # Drop cash_only from groups
    op.drop_column('groups', 'cash_only')
    
    # Drop foreign key and columns from payments
    op.drop_constraint('fk_payments_marked_paid_by', 'payments', type_='foreignkey')
    op.drop_column('payments', 'marked_paid_by')
    op.drop_column('payments', 'payment_type')

