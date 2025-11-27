"""add kyc fields to users table

Revision ID: 20251022_add_kyc_fields
Revises: 20251022_create_otp_codes_table
Create Date: 2025-10-22 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251022_add_kyc_fields'
down_revision = '20251022_create_otp_codes_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add KYC verification fields to users table."""
    # Add kyc_verified column with default False
    op.add_column('users', sa.Column('kyc_verified', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add kyc_verified_at column (nullable)
    op.add_column('users', sa.Column('kyc_verified_at', sa.DateTime(), nullable=True))
    
    # Add kyc_provider column (nullable)
    op.add_column('users', sa.Column('kyc_provider', sa.String(), nullable=True))


def downgrade() -> None:
    """Remove KYC verification fields from users table."""
    op.drop_column('users', 'kyc_provider')
    op.drop_column('users', 'kyc_verified_at')
    op.drop_column('users', 'kyc_verified')

