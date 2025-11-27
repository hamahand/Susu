"""add_group_privacy_settings

Revision ID: a1b2c3d4e5f6
Revises: 3c445a1e12a8
Create Date: 2025-01-26 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '3c445a1e12a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add privacy settings columns to groups table
    op.add_column('groups', sa.Column('show_alias_to_members', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('groups', sa.Column('show_real_name_to_members', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('groups', sa.Column('show_phone_to_members', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove privacy settings columns from groups table
    op.drop_column('groups', 'show_phone_to_members')
    op.drop_column('groups', 'show_real_name_to_members')
    op.drop_column('groups', 'show_alias_to_members')

