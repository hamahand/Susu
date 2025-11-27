"""create otp_codes table

Revision ID: 20251022_create_otp_codes_table
Revises: 20251022_add_email
Create Date: 2025-10-22
"""

from alembic import op
import sqlalchemy as sa


revision = '20251022_create_otp_codes_table'
down_revision = '20251022_add_email'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'otp_codes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('phone_number', sa.String(), nullable=False, index=True),
        sa.Column('code_hash', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('attempts_left', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('otp_codes')


