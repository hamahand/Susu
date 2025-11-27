"""add payment preferences table

Revision ID: 20251022_payment_prefs
Revises: 20251022_invitations
Create Date: 2025-10-22 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251022_payment_prefs'
down_revision = '20251022_invitations'
branch_labels = None
depends_on = None


def upgrade():
    # Create payment_preferences table
    op.create_table(
        'payment_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('payment_method', sa.String(length=20), nullable=False, server_default='manual'),
        sa.Column('auto_pay_enabled', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('auto_pay_day', sa.Integer(), nullable=True),
        sa.Column('send_payment_reminders', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('reminder_days_before', sa.Integer(), nullable=True, server_default='3'),
        sa.Column('momo_consent_given', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('momo_consent_date', sa.DateTime(), nullable=True),
        sa.Column('oauth_auth_req_id', sa.String(length=255), nullable=True),
        sa.Column('oauth_expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_payment_preferences_user_id')
    )
    
    # Create index on user_id for faster lookups
    op.create_index('ix_payment_preferences_user_id', 'payment_preferences', ['user_id'])
    
    # Create index on payment_method for analytics
    op.create_index('ix_payment_preferences_method', 'payment_preferences', ['payment_method'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_payment_preferences_method', table_name='payment_preferences')
    op.drop_index('ix_payment_preferences_user_id', table_name='payment_preferences')
    
    # Drop table
    op.drop_table('payment_preferences')

